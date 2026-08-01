#!/usr/bin/env python3
"""
tech-stack-collector v2.1
=========================
Collect server technical stack information for CV/resume building.

Self-contained (stdlib only). Two ways to run:
  1. Local:   python3 collector.py [--output-dir /path]
  2. Via SSH: see remote_runner.py

Safe mode is the default. Use --full only when you understand that hostnames,
ports, repository paths/remotes, cron entries, and environment data are sensitive.

Output: Structured Markdown → stdout (streaming) + local file.
"""

from __future__ import annotations

import argparse
import datetime
import os
import platform
import re
import shlex
import socket
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import List, Optional, Tuple

# ── Config ──────────────────────────────────────────────────────────────────
VERSION = "2.1"
CMD_TIMEOUT = 8          # seconds per shell command
MAX_WORKERS = 10         # parallel command threads
GIT_SCAN_DIRS = ["/home", "/root", "/srv", "/var/www", "/opt"]
GIT_SCAN_DEPTH = 4
ANSI_ESCAPE = re.compile(r"\x1b\[[0-?]*[ -/]*[@-~]")


# ── Helpers ─────────────────────────────────────────────────────────────────
def run(cmd: str, timeout: int = CMD_TIMEOUT) -> str:
    """Execute *cmd* in shell, return stdout (empty on failure)."""
    try:
        r = subprocess.run(
            cmd, shell=True, capture_output=True, text=True,
            timeout=timeout, env={**os.environ, "LC_ALL": "C", "LANG": "C"},
        )
        return ANSI_ESCAPE.sub("", r.stdout).strip()
    except Exception:
        return ""


UNUSABLE_OUTPUT_MARKERS = (
    "command not found",
    "no such file",
    "not found",
    "permission denied",
    "traceback",
    "exception:",
    "error:",
    "fatal:",
    "usage:",
    "warning",
    "deprecated",
    "<module>",
)


def first_usable_line(output: str, limit: int = 80) -> str:
    """Return the first plausible version line, excluding shell/error noise."""
    for raw_line in output.splitlines():
        line = ANSI_ESCAPE.sub("", raw_line).strip()
        if (
            line
            and not line.startswith("File \"")
            and not re.match(r"^(?:from\s+\S+\s+import|import\s+\S+)", line)
            and not any(marker in line.lower() for marker in UNUSABLE_OUTPUT_MARKERS)
        ):
            return line[:limit]
    return ""


def has(name: str) -> bool:
    if not re.fullmatch(r"[A-Za-z0-9_.+-]+", name):
        return False
    return run(f"command -v {name}") != ""


def emit(text: str) -> None:
    """Print one line with immediate flush (streaming feel)."""
    print(text, flush=True)


def md_table(headers: List[str], rows: List[List[str]]) -> str:
    if not rows:
        return ""
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    for row in rows:
        cells = [str(c).replace("|", "∣").replace("\n", " ")[:120] for c in row]
        while len(cells) < len(headers):
            cells.append("—")
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


def md_bullets(items: List[str]) -> str:
    return "\n".join(f"- {i}" for i in items if i.strip())


def md_table_rows(markdown: str) -> list[list[str]]:
    """Return Markdown table data rows without headers or separator cells."""
    rows: list[list[str]] = []
    for line in markdown.splitlines():
        if not line.strip().startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if not cells or all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells):
            continue
        rows.append(cells)
    return rows[1:] if rows else []


# ── Collectors ──────────────────────────────────────────────────────────────
# Each returns (section_title, markdown_content).
# Content == "" means section is skipped in output.

def collect_system(include_sensitive: bool = False) -> Tuple[str, str]:
    hostname = socket.gethostname()
    pretty = ""
    for line in run("cat /etc/os-release 2>/dev/null").split("\n"):
        if line.startswith("PRETTY_NAME="):
            pretty = line.split("=", 1)[1].strip('"')
    kernel = run("uname -r")
    arch = platform.machine()
    cpus = run("nproc") or str(os.cpu_count() or "?")
    model = ""
    m = run("lscpu 2>/dev/null | grep -i 'model name'")
    if m:
        model = m.split(":", 1)[-1].strip()
    mem = run("free -h 2>/dev/null | awk '/^Mem:/{print $2\" total, \"$3\" used, \"$7\" avail\"}'")
    disk = run("df -h / 2>/dev/null | awk 'NR==2{print $2\" total, \"$3\" used, \"$5\" usage\"}'")
    uptime = run("uptime -p 2>/dev/null") or run("uptime | sed 's/.*up/up/'")
    lines = [
        "- **Hostname:** [redacted in safe mode]",
        f"- **OS family:** {platform.system() or 'unknown'}",
        f"- **Arch:** {arch}",
    ]
    if include_sensitive:
        lines = [
            f"- **Hostname:** {hostname}",
            f"- **OS:** {pretty or platform.platform()}",
            f"- **Kernel:** {kernel}" if kernel else "",
            f"- **Arch:** {arch}",
            f"- **CPU:** {cpus} cores" + (f" — {model}" if model else ""),
            f"- **Memory:** {mem}" if mem else "",
            f"- **Disk (/):** {disk}" if disk else "",
            f"- **Uptime:** {uptime}" if uptime else "",
        ]
    return "System", "\n".join(l for l in lines if l)


def collect_docker(safe: bool = True) -> Tuple[str, str]:
    if not has("docker") and not has("podman"):
        return "Docker / Containers", ""
    engine = "docker" if has("docker") else "podman"
    parts: list[str] = []

    # Names, ports, volumes, and networks may reveal internal topology.
    if not safe:
        ps = run(f"{engine} ps --format '{{{{.Names}}}}\\t{{{{.Image}}}}\\t{{{{.Ports}}}}\\t{{{{.Status}}}}' 2>/dev/null")
        if ps:
            rows = [line.split("\t") for line in ps.split("\n") if line.strip()]
            parts.append("### Running Containers\n\n" +
                         md_table(["Name", "Image", "Ports", "Status"], rows))
        else:
            norun = run(f"{engine} ps -q 2>/dev/null")
            parts.append("### Running Containers\n\n" +
                         ("_None running_" if norun == "" else "_No permission_"))

    # Images
    imgs = run(f"{engine} images --format '{{{{.Repository}}}}:{{{{.Tag}}}}\\t{{{{.Size}}}}' 2>/dev/null | head -30")
    if imgs:
        rows = [line.split("\t") for line in imgs.split("\n") if line.strip()]
        if safe:
            discovered = TagStore()
            for row in rows:
                discovered.resolve_docker_image(row[0])
            technologies = [
                [category, name]
                for category, names in discovered.items()
                for name in sorted(names)
            ]
            parts.append(
                "### Image inventory\n\n"
                + (md_table(["Category", "Technology"], technologies) + "\n\n" if technologies else "")
                + f"_{len(rows)} images scanned; raw names, registries, and sizes omitted in safe mode_"
            )
        else:
            parts.append("### Images\n\n" + md_table(["Image", "Size"], rows))

    if not safe:
        compose = run("docker compose ls --format 'table' 2>/dev/null | head -20")
        if compose and "NAME" in compose:
            parts.append(f"### Compose Projects\n\n```\n{compose}\n```")

        vols = run(f"{engine} volume ls --format '{{{{.Name}}}}' 2>/dev/null | head -20")
        if vols:
            parts.append("### Volumes\n\n" + md_bullets(vols.split("\n")))

        nets = run(f"{engine} network ls --format '{{{{.Name}}}}\\t{{{{.Driver}}}}' 2>/dev/null")
        if nets:
            rows = [l.split("\t") for l in nets.split("\n")
                    if l.strip() and l.split("\t")[0] not in ("bridge", "host", "none")]
            if rows:
                parts.append("### Custom Networks\n\n" + md_table(["Name", "Driver"], rows))

    return "Docker / Containers", "\n\n".join(parts)


def collect_languages() -> Tuple[str, str]:
    checks = [
        ("Python",   "python3 --version 2>&1 || python --version 2>&1"),
        ("Node.js",  "node --version 2>&1"),
        ("Java",     "java --version 2>&1 | head -1"),
        ("Go",       "go version 2>&1"),
        ("Rust",     "rustc --version 2>&1"),
        ("Ruby",     "ruby --version 2>&1"),
        ("PHP",      "php --version 2>&1 | head -1"),
        (".NET",     "dotnet --version 2>&1"),
        ("GCC",      "gcc --version 2>&1 | head -1"),
        ("G++",      "g++ --version 2>&1 | head -1"),
        ("Make",     "make --version 2>&1 | head -1"),
        ("CMake",    "cmake --version 2>&1 | head -1"),
        ("Perl",     "perl -e 'print \"Perl $^V\\n\"' 2>&1"),
        ("Lua",      "lua -v 2>&1 || lua5.4 -v 2>&1"),
        ("R",        "R --version 2>&1 | head -1"),
        ("Swift",    "swift --version 2>&1 | head -1"),
        ("Kotlin",   "kotlin -version 2>&1 | head -1"),
        ("Zig",      "zig version 2>&1"),
        ("Nim",      "nim --version 2>&1 | head -1"),
        ("Deno",     "deno --version 2>&1 | head -1"),
        ("Bun",      "bun --version 2>&1"),
    ]
    def _chk(name: str, cmd: str) -> Optional[List[str]]:
        v = run(cmd, timeout=5)
        version = first_usable_line(v)
        if version:
            return [name, version]
        return None

    rows: list[list[str]] = []
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        futs = {pool.submit(_chk, n, c): n for n, c in checks}
        for f in as_completed(futs):
            r = f.result()
            if r:
                rows.append(r)
    rows.sort(key=lambda x: x[0].lower())
    return "Programming Languages", md_table(["Language", "Version"], rows) if rows else ""


def collect_package_managers(include_details: bool = False) -> Tuple[str, str]:
    parts: list[str] = []
    summaries: list[str] = []

    # pip
    pip_out = run("pip3 list --format=columns 2>/dev/null | tail -n +3 | head -50") \
           or run("pip list --format=columns 2>/dev/null | tail -n +3 | head -50")
    if pip_out:
        cnt = run("pip3 list 2>/dev/null | tail -n +3 | wc -l")
        summaries.append(f"pip: {cnt.strip() or 'unknown'} packages; names omitted")
        if include_details:
            parts.append(f"### pip ({cnt.strip()} packages, showing first 50)\n\n```\n{pip_out}\n```")

    # npm global
    npm_out = run("npm -g list --depth=0 2>/dev/null | tail -n +2")
    if npm_out and "empty" not in npm_out.lower():
        summaries.append(f"npm global: {len(npm_out.splitlines())} entries; names omitted")
        if include_details:
            parts.append(f"### npm (global)\n\n```\n{npm_out}\n```")

    # cargo
    if has("cargo"):
        cargo_out = run("cargo install --list 2>/dev/null | head -30")
        if cargo_out:
            summaries.append("cargo: installed packages detected; names omitted")
            if include_details:
                parts.append(f"### cargo installed\n\n```\n{cargo_out}\n```")

    # go binaries
    gobin = Path.home() / "go" / "bin"
    if gobin.is_dir():
        bins = sorted(f.name for f in gobin.iterdir() if f.is_file())[:30]
        if bins:
            summaries.append(f"Go binaries: {len(bins)} detected; names omitted")
            if include_details:
                parts.append("### Go binaries (~/go/bin)\n\n" + md_bullets(bins))

    # snap
    snap_out = run("snap list 2>/dev/null | tail -n +2 | head -25")
    if snap_out:
        summaries.append(f"snap: {len(snap_out.splitlines())} entries; names omitted")
        if include_details:
            parts.append(f"### snap\n\n```\n{snap_out}\n```")

    # gem
    if has("gem"):
        gem_out = run("gem list --local --no-details 2>/dev/null | head -30")
        if gem_out:
            summaries.append(f"gem: {len(gem_out.splitlines())} entries; names omitted")
            if include_details:
                parts.append(f"### gem\n\n```\n{gem_out}\n```")

    # composer
    if has("composer"):
        comp_out = run("composer global show --name-only 2>/dev/null | head -20")
        if comp_out:
            summaries.append(f"composer global: {len(comp_out.splitlines())} entries; names omitted")
            if include_details:
                parts.append(f"### composer (global)\n\n```\n{comp_out}\n```")

    content = "\n\n".join(parts) if include_details else md_bullets(summaries)
    return "Package Managers", content


def collect_key_dirs() -> Tuple[str, str]:
    parts: list[str] = []
    scan = [
        ("/opt",             "Installed in /opt"),
        ("/usr/local/bin",   "/usr/local/bin"),
        ("/usr/local/sbin",  "/usr/local/sbin"),
        ("/srv",             "Services in /srv"),
        ("/var/www",         "Web roots in /var/www"),
    ]
    for path, label in scan:
        if os.path.isdir(path):
            try:
                entries = sorted(os.listdir(path))[:50]
                if entries:
                    parts.append(f"### {label}\n\n" + md_bullets(entries))
            except PermissionError:
                parts.append(f"### {label}\n\n_Permission denied_")

    # Home sub-directories of interest
    home = Path.home()
    for d in ("projects", "repos", "workspace", "code", "dev", "src", "work", "apps"):
        p = home / d
        if p.is_dir():
            try:
                entries = sorted(e.name for e in p.iterdir() if e.is_dir())[:30]
                if entries:
                    parts.append(f"### ~/{d}/\n\n" + md_bullets(entries))
            except PermissionError:
                pass

    local_bin = home / ".local" / "bin"
    if local_bin.is_dir():
        try:
            entries = sorted(os.listdir(local_bin))[:40]
            if entries:
                parts.append("### ~/.local/bin\n\n" + md_bullets(entries))
        except PermissionError:
            pass

    return "Key Directories", "\n\n".join(parts) if parts else ""


def collect_services(safe: bool = True) -> Tuple[str, str]:
    raw = run("systemctl list-units --type=service --state=running --no-pager --plain 2>/dev/null "
              "| awk '{print $1}' | grep '\\.service$' | sort")
    if not raw:
        return "Running Services", ""

    # Separate notable vs system-default services
    boring_prefixes = {
        "accounts-daemon", "acpid", "apparmor", "auditd", "blk-availability",
        "console-setup", "cron", "dbus", "getty@", "ifup@", "irqbalance",
        "keyboard-setup", "kmod", "lvm2", "multipathd", "networking",
        "packagekit", "polkit", "rsyslog", "serial-getty@", "ssh", "sshd",
        "systemd-", "udev", "udisks2", "unattended-upgrades",
        "user@", "user-runtime-dir@",
    }
    services = [s.strip() for s in raw.split("\n") if s.strip()]
    notable, sys_count = [], 0
    for s in services:
        if any(s.startswith(b) for b in boring_prefixes):
            sys_count += 1
        else:
            notable.append(s)

    parts: list[str] = []
    if safe:
        discovered = TagStore()
        for service in notable:
            discovered.resolve_service(service)
        technologies = discovered.flat_tags()
        if technologies:
            parts.append("### Recognized technologies\n\n" + md_bullets(technologies))
        parts.append(
            f"_{len(services)} running services scanned; raw unit names omitted in safe mode_"
        )
    else:
        if notable:
            parts.append("### Notable\n\n" + md_bullets(notable))
        parts.append(f"\n_{sys_count} standard system services omitted_")
    return "Running Services", "\n".join(parts)


def collect_ports() -> Tuple[str, str]:
    raw = run("ss -tlnp 2>/dev/null | tail -n +2") or run("netstat -tlnp 2>/dev/null | tail -n +2")
    if not raw:
        return "Listening Ports", ""
    rows: list[list[str]] = []
    for line in raw.split("\n"):
        cols = line.split()
        if len(cols) < 5:
            continue
        addr = cols[3]
        port = addr.rsplit(":", 1)[-1] if ":" in addr else addr
        proc_match = re.search(r'users:\(\("([^"]+)"', line)
        proc = proc_match.group(1) if proc_match else "—"
        rows.append([port, addr, proc])
    rows.sort(key=lambda x: int(x[0]) if x[0].isdigit() else 99999)
    return "Listening Ports", md_table(["Port", "Bind Address", "Process"], rows)


def collect_databases() -> Tuple[str, str]:
    checks = [
        ("PostgreSQL",      "psql --version 2>&1",              "postgres"),
        ("MySQL / MariaDB", "mysql --version 2>&1",             "mysql"),
        ("Redis",           "redis-server --version 2>&1",      "redis-server"),
        ("MongoDB",         "mongod --version 2>&1 | head -1",  "mongod"),
        ("SQLite3",         "sqlite3 --version 2>&1",           "sqlite3"),
        ("InfluxDB",        "influx version 2>&1",              "influxd"),
        ("CockroachDB",     "cockroach version 2>&1 | head -1", "cockroach"),
        ("ClickHouse",      "clickhouse-client --version 2>&1", "clickhouse"),
    ]
    rows: list[list[str]] = []
    for name, cmd, proc in checks:
        v = run(cmd, timeout=5)
        version = first_usable_line(v)
        if version:
            running = "✓ running" if run(f"pgrep -x {proc} 2>/dev/null") else "installed"
            rows.append([name, version, running])
    return "Databases", md_table(["Database", "Version", "Status"], rows) if rows else ""


def collect_web_servers(include_sites: bool = False) -> Tuple[str, str]:
    parts: list[str] = []
    for name, ver_cmd, sites_cmd in [
        ("Nginx",   "nginx -v 2>&1",                       "ls /etc/nginx/sites-enabled/ 2>/dev/null"),
        ("Apache",  "apache2 -v 2>&1 | head -1",           "ls /etc/apache2/sites-enabled/ 2>/dev/null"),
        ("Caddy",   "caddy version 2>&1",                   ""),
        ("Traefik", "traefik version 2>&1 | head -1",       ""),
        ("HAProxy", "haproxy -v 2>&1 | head -1",            ""),
    ]:
        v = run(ver_cmd, timeout=5)
        version = first_usable_line(v)
        if version:
            line = f"- **{name}:** {version}"
            if sites_cmd and include_sites:
                sites = run(sites_cmd)
                if sites:
                    line += f"  (sites: {', '.join(sites.split())})"
            parts.append(line)
    return "Web Servers", "\n".join(parts) if parts else ""


def collect_devops() -> Tuple[str, str]:
    tools = [
        ("Terraform",      "terraform --version 2>&1 | head -1"),
        ("OpenTofu",       "tofu --version 2>&1 | head -1"),
        ("Ansible",        "ansible --version 2>&1 | head -1"),
        ("kubectl",        "kubectl version --client 2>/dev/null | head -1"),
        ("Helm",           "helm version --short 2>&1"),
        ("k3s",            "k3s --version 2>&1"),
        ("Minikube",       "minikube version --short 2>&1"),
        ("k9s",            "k9s version --short 2>&1 | head -1"),
        ("AWS CLI",        "aws --version 2>&1"),
        ("Azure CLI",      "az version 2>&1 | head -1"),
        ("gcloud",         "gcloud --version 2>&1 | head -1"),
        ("Vagrant",        "vagrant --version 2>&1"),
        ("Packer",         "packer --version 2>&1"),
        ("Pulumi",         "pulumi version 2>&1"),
        ("Docker Compose", "docker compose version 2>&1"),
        ("Podman",         "podman --version 2>&1"),
        ("Buildah",        "buildah --version 2>&1"),
        ("Trivy",          "trivy --version 2>&1 | head -1"),
        ("Vault",          "vault --version 2>&1"),
        ("Consul",         "consul --version 2>&1 | head -1"),
    ]
    def _chk(name: str, cmd: str) -> Optional[List[str]]:
        v = run(cmd, timeout=5)
        version = first_usable_line(v)
        if version:
            return [name, version]
        return None

    rows: list[list[str]] = []
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        futs = {pool.submit(_chk, n, c): n for n, c in tools}
        for f in as_completed(futs):
            r = f.result()
            if r:
                rows.append(r)
    rows.sort(key=lambda x: x[0].lower())
    return "Cloud & DevOps Tools", md_table(["Tool", "Version"], rows) if rows else ""


def collect_cli_tools() -> Tuple[str, str]:
    tools = [
        ("git",         "git --version 2>&1"),
        ("curl",        "curl --version 2>&1 | head -1"),
        ("wget",        "wget --version 2>&1 | head -1"),
        ("rsync",       "rsync --version 2>&1 | head -1"),
        ("tmux",        "tmux -V 2>&1"),
        ("screen",      "screen --version 2>&1 | head -1"),
        ("htop",        "htop --version 2>&1"),
        ("btop",        "btop --version 2>&1 | head -1"),
        ("neovim",      "nvim --version 2>&1 | head -1"),
        ("vim",         "vim --version 2>&1 | head -1"),
        ("jq",          "jq --version 2>&1"),
        ("yq",          "yq --version 2>&1"),
        ("fzf",         "fzf --version 2>&1"),
        ("ripgrep",     "rg --version 2>&1 | head -1"),
        ("fd",          "fd --version 2>&1 || fdfind --version 2>&1"),
        ("bat",         "bat --version 2>&1 || batcat --version 2>&1"),
        ("exa/eza",     "eza --version 2>&1 || exa --version 2>&1 | head -1"),
        ("zoxide",      "zoxide --version 2>&1"),
        ("ffmpeg",      "ffmpeg -version 2>&1 | head -1"),
        ("ImageMagick", "magick --version 2>&1 | head -1 || convert --version 2>&1 | head -1"),
        ("pandoc",      "pandoc --version 2>&1 | head -1"),
        ("tree",        "tree --version 2>&1 | head -1"),
        ("strace",      "strace --version 2>&1 | head -1"),
        ("lsof",        "lsof -v 2>&1 | head -1"),
    ]
    def _chk(name: str, cmd: str) -> Optional[List[str]]:
        v = run(cmd, timeout=5)
        version = first_usable_line(v)
        if version:
            return [name, version]
        return None

    rows: list[list[str]] = []
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        futs = {pool.submit(_chk, n, c): n for n, c in tools}
        for f in as_completed(futs):
            r = f.result()
            if r:
                rows.append(r)
    rows.sort(key=lambda x: x[0].lower())
    return "CLI & Utility Tools", md_table(["Tool", "Version"], rows) if rows else ""


def collect_network_security() -> Tuple[str, str]:
    tools = [
        ("WireGuard",  "wg --version 2>&1 | head -1"),
        ("OpenVPN",    "openvpn --version 2>&1 | head -1"),
        ("iptables",   "iptables --version 2>&1"),
        ("nftables",   "nft --version 2>&1"),
        ("UFW",        "ufw version 2>&1"),
        ("Certbot",    "certbot --version 2>&1"),
        ("Fail2ban",   "fail2ban-server --version 2>&1"),
        ("CrowdSec",   "cscli version 2>&1 | head -1"),
    ]
    found: list[str] = []
    for name, cmd in tools:
        v = run(cmd, timeout=5)
        version = first_usable_line(v)
        if version:
            found.append(f"- **{name}:** {version}")
    return "Network & Security", "\n".join(found) if found else ""


def collect_git_repos() -> Tuple[str, str]:
    repos: list[list[str]] = []
    for base in GIT_SCAN_DIRS:
        if not os.path.isdir(base):
            continue
        res = run(f"find {base} -maxdepth {GIT_SCAN_DEPTH} -name .git -type d 2>/dev/null | head -25",
                  timeout=15)
        if not res:
            continue
        for git_dir in res.split("\n"):
            repo = os.path.dirname(git_dir.strip())
            if not repo:
                continue
            quoted_repo = shlex.quote(repo)
            remote = run(f"git -C {quoted_repo} remote get-url origin 2>/dev/null")
            branch = run(f"git -C {quoted_repo} branch --show-current 2>/dev/null")
            repos.append([repo, remote or "local-only", branch or "—"])
    return "Git Repositories", md_table(["Path", "Remote", "Branch"], repos) if repos else ""


def collect_cron() -> Tuple[str, str]:
    parts: list[str] = []
    ct = run("crontab -l 2>/dev/null")
    if ct and "no crontab" not in ct.lower():
        parts.append(f"### User Crontab\n\n```\n{ct}\n```")
    sys_cron = run("ls /etc/cron.d/ 2>/dev/null")
    if sys_cron:
        parts.append("### /etc/cron.d/\n\n" + md_bullets(sys_cron.split()))
    timers = run("systemctl list-timers --no-pager --plain 2>/dev/null | head -20")
    if timers:
        parts.append(f"### Systemd Timers\n\n```\n{timers}\n```")
    return "Scheduled Tasks", "\n\n".join(parts) if parts else ""


def collect_virtualization() -> Tuple[str, str]:
    vtype = run("systemd-detect-virt 2>/dev/null") or "bare-metal / unknown"
    parts = [f"**Platform:** {vtype}"]
    for name, cmd in [
        ("KVM/QEMU", "qemu-system-x86_64 --version 2>&1 | head -1"),
        ("libvirt",  "virsh version --daemon 2>&1 | head -3"),
        ("LXC",      "lxc-info --version 2>&1"),
        ("LXD",      "lxd --version 2>&1"),
        ("Incus",    "incus version 2>&1"),
    ]:
        v = run(cmd, timeout=5)
        version = first_usable_line(v)
        if version:
            parts.append(f"- **{name}:** {version}")
    return "Virtualization", "\n".join(parts)


def collect_monitoring() -> Tuple[str, str]:
    checks = [
        ("Prometheus",     "prometheus --version 2>&1 | head -1"),
        ("Grafana",        "grafana-server -v 2>&1 | head -1"),
        ("Telegraf",       "telegraf --version 2>&1"),
        ("Node Exporter",  "node_exporter --version 2>&1 | head -1"),
        ("Zabbix Agent",   "zabbix_agentd --version 2>&1 | head -1"),
        ("Netdata",        "netdata -v 2>&1"),
    ]
    found: list[str] = []
    for name, cmd in checks:
        v = run(cmd, timeout=5)
        version = first_usable_line(v)
        if version:
            found.append(f"- **{name}:** {version}")
    return "Monitoring & Observability", "\n".join(found) if found else ""


def collect_shell_env() -> Tuple[str, str]:
    parts: list[str] = []
    shell = os.environ.get("SHELL", "unknown")
    parts.append(f"**Default shell:** `{shell}`")

    interest = [
        "LANG", "EDITOR", "VISUAL", "TERM", "GOPATH", "GOROOT",
        "JAVA_HOME", "NVM_DIR", "PYENV_ROOT", "CARGO_HOME",
        "VIRTUAL_ENV", "CONDA_DEFAULT_ENV", "DISPLAY", "WAYLAND_DISPLAY",
    ]
    env_lines = [f"- `{k}={v}`" for k in interest if (v := os.environ.get(k))]
    if env_lines:
        parts.append("### Notable Env Vars\n\n" + "\n".join(env_lines))

    for rc in (".bashrc", ".zshrc", ".profile", ".bash_aliases"):
        p = Path.home() / rc
        if p.exists():
            try:
                txt = p.read_text(errors="ignore")
                n_alias = txt.count("\nalias ")
                n_func = len(re.findall(r'\n\w+\s*\(\)\s*\{', txt))
                if n_alias or n_func:
                    parts.append(f"- **{rc}:** {n_alias} aliases, {n_func} functions")
            except Exception:
                pass

    ssh_dir = Path.home() / ".ssh"
    if ssh_dir.is_dir():
        try:
            keys = sorted(f.name for f in ssh_dir.iterdir() if f.suffix == ".pub")
            if keys:
                parts.append("### SSH Public Keys\n\n" + md_bullets(keys))
        except PermissionError:
            pass

    return "Shell Environment", "\n\n".join(parts) if parts else ""


# ── Tag Extractor v2 ────────────────────────────────────────────────────────
# Structured extraction from collector data, not from rendered text.
# Two-layer approach:
#   1. Each collector registers tags into a shared TagStore (domain → tag)
#   2. Docker images get special parsing via a knowledge base
#
# Categories used for AI-friendly output:
#   Containers, Orchestration, Languages, Databases, Caching, MessageBrokers,
#   WebServers, ReverseProxy, Cloud, DevOps, IaC, Monitoring, Networking,
#   Security, CI_CD, Virtualization, Storage, Applications, CLI

class TagStore:
    """Accumulate (category → set of canonical tags) during collection."""

    def __init__(self) -> None:
        self._tags: dict[str, set[str]] = {}

    def add(self, category: str, *names: str) -> None:
        bucket = self._tags.setdefault(category, set())
        for n in names:
            if n:
                bucket.add(n)

    def flat_tags(self) -> list[str]:
        """Return canonical technology names without their source identifiers."""
        return sorted({name for names in self._tags.values() for name in names})

    def items(self) -> list[tuple[str, set[str]]]:
        """Return a stable copy of categorized canonical technologies."""
        return [(category, set(self._tags[category])) for category in sorted(self._tags)]

    # ── Docker image → tag resolution ───────────────────────────────────
    # Maps image-name fragments to (category, canonical_name).
    # Order: longest prefix match wins.
    _IMAGE_MAP: dict[str, tuple[str, str]] = {
        # AI / LLM
        "langgenius/dify":           ("Applications",   "Dify (AI/LLM)"),
        "dify-api":                  ("Applications",   "Dify (AI/LLM)"),
        "dify-web":                  ("Applications",   "Dify (AI/LLM)"),
        "dify-sandbox":              ("Applications",   "Dify (AI/LLM)"),
        "dify-plugin-daemon":        ("Applications",   "Dify (AI/LLM)"),
        "ollama":                    ("Applications",   "Ollama (LLM)"),
        "open-webui":                ("Applications",   "Open WebUI"),
        "localai":                   ("Applications",   "LocalAI"),
        "vllm":                      ("Applications",   "vLLM"),
        "text-generation-inference": ("Applications",   "TGI (HuggingFace)"),
        # Vector DB
        "weaviate":                  ("Databases",      "Weaviate (Vector DB)"),
        "qdrant":                    ("Databases",      "Qdrant (Vector DB)"),
        "milvus":                    ("Databases",      "Milvus (Vector DB)"),
        "chromadb":                  ("Databases",      "ChromaDB"),
        "pinecone":                  ("Databases",      "Pinecone"),
        # Databases
        "postgres":                  ("Databases",      "PostgreSQL"),
        "mysql":                     ("Databases",      "MySQL"),
        "mariadb":                   ("Databases",      "MariaDB"),
        "mongo":                     ("Databases",      "MongoDB"),
        "redis":                     ("Caching",        "Redis"),
        "memcached":                 ("Caching",        "Memcached"),
        "elasticsearch":             ("Databases",      "Elasticsearch"),
        "opensearch":                ("Databases",      "OpenSearch"),
        "clickhouse":                ("Databases",      "ClickHouse"),
        "influxdb":                  ("Databases",      "InfluxDB"),
        "timescaledb":               ("Databases",      "TimescaleDB"),
        "cockroachdb":               ("Databases",      "CockroachDB"),
        "mssql":                     ("Databases",      "SQL Server"),
        "cassandra":                 ("Databases",      "Cassandra"),
        "neo4j":                     ("Databases",      "Neo4j"),
        "arangodb":                  ("Databases",      "ArangoDB"),
        # Message Brokers / IoT
        "rabbitmq":                  ("MessageBrokers", "RabbitMQ"),
        "emqx":                      ("MessageBrokers", "EMQX (MQTT)"),
        "eclipse-mosquitto":         ("MessageBrokers", "Mosquitto (MQTT)"),
        "mosquitto":                 ("MessageBrokers", "Mosquitto (MQTT)"),
        "nats":                      ("MessageBrokers", "NATS"),
        "kafka":                     ("MessageBrokers", "Kafka"),
        "redpanda":                  ("MessageBrokers", "Redpanda"),
        # Web / Proxy
        "nginx":                     ("ReverseProxy",   "Nginx"),
        "openresty":                 ("ReverseProxy",   "OpenResty (Nginx)"),
        "caddy":                     ("ReverseProxy",   "Caddy"),
        "traefik":                   ("ReverseProxy",   "Traefik"),
        "haproxy":                   ("ReverseProxy",   "HAProxy"),
        "httpd":                     ("WebServers",     "Apache HTTPD"),
        "squid":                     ("ReverseProxy",   "Squid Proxy"),
        # Applications
        "sharelatex":                ("Applications",   "Overleaf (LaTeX)"),
        "overleaf":                  ("Applications",   "Overleaf (LaTeX)"),
        "erpnext":                   ("Applications",   "ERPNext"),
        "frappe":                    ("Applications",   "ERPNext (Frappe)"),
        "invoiceninja":              ("Applications",   "Invoice Ninja"),
        "opensign":                  ("Applications",   "OpenSign"),
        "opensignserver":            ("Applications",   "OpenSign"),
        "nextcloud":                 ("Applications",   "Nextcloud"),
        "gitea":                     ("Applications",   "Gitea"),
        "gitlab":                    ("Applications",   "GitLab"),
        "drone":                     ("CI_CD",          "Drone CI"),
        "jenkins":                   ("CI_CD",          "Jenkins"),
        "woodpecker":                ("CI_CD",          "Woodpecker CI"),
        "sonarqube":                 ("Applications",   "SonarQube"),
        "mattermost":                ("Applications",   "Mattermost"),
        "rocket.chat":               ("Applications",   "Rocket.Chat"),
        "vaultwarden":               ("Applications",   "Vaultwarden"),
        "bitwarden":                 ("Applications",   "Bitwarden"),
        "ghostcms":                  ("Applications",   "Ghost CMS"),
        "ghost":                     ("Applications",   "Ghost CMS"),
        "wordpress":                 ("Applications",   "WordPress"),
        "joomla":                    ("Applications",   "Joomla"),
        "plausible":                 ("Applications",   "Plausible Analytics"),
        "matomo":                    ("Applications",   "Matomo Analytics"),
        "umami":                     ("Applications",   "Umami Analytics"),
        "uptime-kuma":               ("Monitoring",     "Uptime Kuma"),
        "grafana":                   ("Monitoring",     "Grafana"),
        "prometheus":                ("Monitoring",     "Prometheus"),
        "loki":                      ("Monitoring",     "Grafana Loki"),
        "telegraf":                  ("Monitoring",     "Telegraf"),
        "zabbix":                    ("Monitoring",     "Zabbix"),
        "netdata":                   ("Monitoring",     "Netdata"),
        "portainer":                 ("Containers",     "Portainer"),
        "watchtower":                ("Containers",     "Watchtower"),
        "home-assistant":            ("Applications",   "Home Assistant"),
        "hass":                      ("Applications",   "Home Assistant"),
        "node-red":                  ("Applications",   "Node-RED"),
        "zigbee2mqtt":               ("Applications",   "Zigbee2MQTT"),
        "aria2":                     ("Applications",   "Aria2 (Downloader)"),
        "transmission":              ("Applications",   "Transmission (BT)"),
        "qbittorrent":               ("Applications",   "qBittorrent"),
        "jellyfin":                  ("Applications",   "Jellyfin"),
        "plex":                      ("Applications",   "Plex"),
        "minio":                     ("Storage",        "MinIO (S3)"),
        "registry":                  ("Containers",     "Docker Registry"),
        "verdaccio":                 ("Applications",   "Verdaccio (npm)"),
        "syncthing":                 ("Applications",   "Syncthing"),
        "filebrowser":               ("Applications",   "File Browser"),
        "v2ray":                     ("Networking",     "V2Ray"),
        "xray":                      ("Networking",     "Xray"),
        "clash":                     ("Networking",     "Clash"),
        "sing-box":                  ("Networking",     "sing-box"),
        "gost":                      ("Networking",     "GOST"),
        "mtranserver":               ("Applications",   "MTranServer (Translation)"),
        "dnsmgr":                    ("Networking",     "DNSMgr"),
        "adguard":                   ("Networking",     "AdGuard Home"),
        "pihole":                    ("Networking",     "Pi-hole"),
        "coredns":                   ("Networking",     "CoreDNS"),
        "epic-awesome-gamer":        ("Applications",   "Epic Games Claimer"),
    }

    def resolve_docker_image(self, image: str) -> None:
        """Parse a Docker image string and add matching tags."""
        # image format: [registry/]org/name:tag  or  name:tag
        # strip tag
        img_lower = image.lower().split(":")[0].strip()
        # try progressively shorter suffixes for matching
        parts = img_lower.split("/")
        # check full path, then org/name, then just name
        candidates = [
            img_lower,
            "/".join(parts[-2:]) if len(parts) >= 2 else "",
            parts[-1],
        ]
        matched = False
        for c in candidates:
            if not c:
                continue
            for key, (cat, tag) in self._IMAGE_MAP.items():
                if key in c:
                    self.add(cat, tag)
                    matched = True
                    break
            if matched:
                break
        # Always tag Docker itself
        self.add("Containers", "Docker")

    def resolve_service(self, svc: str) -> None:
        """Extract tech from a systemd service name."""
        svc_lower = svc.lower().replace(".service", "")
        _SVC_MAP = {
            "docker":       ("Containers",     "Docker"),
            "containerd":   ("Containers",     "containerd"),
            "podman":       ("Containers",     "Podman"),
            "k3s":          ("Orchestration",  "K3s"),
            "kubelet":      ("Orchestration",  "Kubernetes"),
            "tailscale":    ("Networking",      "Tailscale"),
            "wireguard":    ("Networking",      "WireGuard"),
            "openvpn":      ("Networking",      "OpenVPN"),
            "nginx":        ("ReverseProxy",   "Nginx"),
            "caddy":        ("ReverseProxy",   "Caddy"),
            "apache2":      ("WebServers",     "Apache"),
            "httpd":        ("WebServers",     "Apache"),
            "postgresql":   ("Databases",      "PostgreSQL"),
            "mysql":        ("Databases",      "MySQL"),
            "mariadb":      ("Databases",      "MariaDB"),
            "mongod":       ("Databases",      "MongoDB"),
            "redis":        ("Caching",        "Redis"),
            "fail2ban":     ("Security",       "Fail2ban"),
            "crowdsec":     ("Security",       "CrowdSec"),
            "prometheus":   ("Monitoring",     "Prometheus"),
            "grafana":      ("Monitoring",     "Grafana"),
            "telegraf":     ("Monitoring",     "Telegraf"),
            "netdata":      ("Monitoring",     "Netdata"),
            "rclone":       ("Storage",        "rclone"),
            "smbd":         ("Networking",      "Samba (SMB)"),
            "samba":        ("Networking",      "Samba (SMB)"),
            "nfs":          ("Storage",        "NFS"),
            "libvirtd":     ("Virtualization", "libvirt"),
            "vnstat":       ("Monitoring",     "vnStat"),
            "nezha":        ("Monitoring",     "Nezha (Probe)"),
            "1panel":       ("Applications",   "1Panel"),
            "frp":          ("Networking",      "frp (Tunnel)"),
        }
        for key, (cat, tag) in _SVC_MAP.items():
            if key in svc_lower:
                self.add(cat, tag)
                return

    def resolve_tool(self, name: str, category: str) -> None:
        """Add a detected CLI tool / language."""
        # Normalize common names
        _NORM = {
            "gcc": "GCC", "g++": "G++", "make": "GNU Make", "cmake": "CMake",
            "python": "Python", "node.js": "Node.js", "java": "Java",
            "go": "Go", "rust": "Rust", "ruby": "Ruby", "php": "PHP",
            ".net": ".NET", "perl": "Perl", "lua": "Lua", "r": "R",
            "swift": "Swift", "kotlin": "Kotlin", "zig": "Zig",
            "nim": "Nim", "deno": "Deno", "bun": "Bun",
            "terraform": "Terraform", "opentofu": "OpenTofu",
            "ansible": "Ansible", "kubectl": "kubectl",
            "helm": "Helm", "k3s": "K3s", "k9s": "K9s",
            "minikube": "Minikube",
            "aws cli": "AWS CLI", "azure cli": "Azure CLI", "gcloud": "GCP CLI",
            "vagrant": "Vagrant", "packer": "Packer", "pulumi": "Pulumi",
            "docker compose": "Docker Compose", "podman": "Podman",
            "buildah": "Buildah", "trivy": "Trivy", "vault": "HashiCorp Vault",
            "consul": "HashiCorp Consul",
            "git": "Git", "curl": "curl", "wget": "wget",
            "tmux": "tmux", "neovim": "Neovim", "vim": "Vim",
            "jq": "jq", "yq": "yq", "fzf": "fzf",
            "ripgrep": "ripgrep", "fd": "fd", "bat": "bat",
            "ffmpeg": "FFmpeg", "imagemagick": "ImageMagick",
            "pandoc": "Pandoc", "rsync": "rsync",
            "wireguard": "WireGuard", "openvpn": "OpenVPN",
            "iptables": "iptables", "nftables": "nftables",
            "ufw": "UFW", "certbot": "Certbot (Let's Encrypt)",
            "fail2ban": "Fail2ban", "crowdsec": "CrowdSec",
            "nginx": "Nginx", "apache": "Apache", "caddy": "Caddy",
            "traefik": "Traefik", "haproxy": "HAProxy",
            "postgresql": "PostgreSQL", "mysql": "MySQL",
            "mariadb": "MariaDB", "redis": "Redis", "mongodb": "MongoDB",
            "sqlite3": "SQLite", "influxdb": "InfluxDB",
            "clickhouse": "ClickHouse", "cockroachdb": "CockroachDB",
            "prometheus": "Prometheus", "grafana": "Grafana",
            "telegraf": "Telegraf", "netdata": "Netdata",
            "node exporter": "Prometheus Node Exporter",
            "zabbix agent": "Zabbix",
            "kvm/qemu": "KVM/QEMU", "libvirt": "libvirt",
            "lxc": "LXC", "lxd": "LXD", "incus": "Incus",
            "htop": "htop", "btop": "btop",
        }
        canonical = _NORM.get(name.lower(), name)
        self.add(category, canonical)

    def resolve_git_repo(self, remote: str) -> None:
        """Extract project info from git remote URL."""
        if not remote or remote == "local-only":
            return
        # github.com/user/repo.git → repo
        m = re.search(r'[/:]([^/]+)/([^/]+?)(?:\.git)?$', remote)
        if not m:
            return
        repo_name = m.group(2).lower()
        _REPO_MAP = {
            "dify":                   ("Applications",   "Dify (AI/LLM)"),
            "smarthome_server":       ("Applications",   "IoT/Smart Home"),
            "bttrackers-updater":     ("Applications",   "BT Tracker Updater"),
            "frappe_docker":          ("Applications",   "ERPNext (Frappe)"),
            "overleaf":               ("Applications",   "Overleaf (LaTeX)"),
            "toolkit":                ("Applications",   "Overleaf (LaTeX)"),
            "czech-visa":             ("Applications",   "Visa Monitor Bot"),
        }
        for key, (cat, tag) in _REPO_MAP.items():
            if key in repo_name:
                self.add(cat, tag)
                return

    # ── Output ──────────────────────────────────────────────────────────
    # Category display order and labels
    _CAT_ORDER = [
        ("Containers",     "🐳 Containers & Orchestration"),
        ("Orchestration",  "🐳 Containers & Orchestration"),
        ("Languages",      "💻 Programming Languages"),
        ("Databases",      "🗄️ Databases"),
        ("Caching",        "⚡ Caching & KV Stores"),
        ("MessageBrokers", "📨 Message Brokers & IoT"),
        ("ReverseProxy",   "🌐 Web & Reverse Proxy"),
        ("WebServers",     "🌐 Web & Reverse Proxy"),
        ("Cloud",          "☁️ Cloud Platforms"),
        ("DevOps",         "🔧 DevOps & IaC"),
        ("IaC",            "🔧 DevOps & IaC"),
        ("CI_CD",          "🚀 CI/CD"),
        ("Monitoring",     "📊 Monitoring & Observability"),
        ("Networking",     "🔗 Networking & DNS"),
        ("Security",       "🛡️ Security"),
        ("Virtualization", "🖥️ Virtualization"),
        ("Storage",        "💾 Storage"),
        ("Applications",   "📦 Self-Hosted Applications"),
        ("CLI",            "🔨 CLI Tooling"),
    ]

    def format_tags(self) -> str:
        if not self._tags:
            return ""

        # Merge categories that share a display label
        merged: dict[str, set[str]] = {}
        seen_cats: set[str] = set()
        for cat, label in self._CAT_ORDER:
            if cat in self._tags and cat not in seen_cats:
                bucket = merged.setdefault(label, set())
                bucket.update(self._tags[cat])
                seen_cats.add(cat)
        # Any remaining un-mapped categories
        for cat, tags in self._tags.items():
            if cat not in seen_cats:
                label = f"🏷️ {cat}"
                merged.setdefault(label, set()).update(tags)

        # Build markdown
        lines: list[str] = []
        flat_all: list[str] = []
        for cat, label in self._CAT_ORDER:
            if label in merged and merged[label]:
                tags_sorted = sorted(merged.pop(label))
                flat_all.extend(tags_sorted)
                lines.append(f"**{label}**")
                lines.append(", ".join(f"`{t}`" for t in tags_sorted))
                lines.append("")
        # Leftover
        for label, tags in sorted(merged.items()):
            if tags:
                tags_sorted = sorted(tags)
                flat_all.extend(tags_sorted)
                lines.append(f"**{label}**")
                lines.append(", ".join(f"`{t}`" for t in tags_sorted))
                lines.append("")

        # Flat summary for quick parsing
        lines.append("---")
        lines.append(f"**All ({len(flat_all)}):** " + ", ".join(f"`{t}`" for t in sorted(set(flat_all))))

        return "\n".join(lines)


# ── Orchestrator ────────────────────────────────────────────────────────────
SECTION_ORDER = [
    "System",
    "Docker / Containers",
    "Programming Languages",
    "Package Managers",
    "Key Directories",
    "Running Services",
    "Listening Ports",
    "Databases",
    "Web Servers",
    "Cloud & DevOps Tools",
    "CLI & Utility Tools",
    "Network & Security",
    "Git Repositories",
    "Scheduled Tasks",
    "Virtualization",
    "Monitoring & Observability",
    "Shell Environment",
]


def build_report(output_dir: str = ".", full: bool = False) -> str:
    hostname = socket.gethostname()
    ts = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

    header = (
        f"# Tech Stack Report\n\n"
        f"- **Host:** {hostname if full else '[redacted in safe mode]'}\n"
        f"- **Date:** {ts}\n"
        f"- **User:** {os.environ.get('USER', os.environ.get('LOGNAME', 'unknown')) if full else '[redacted in safe mode]'}\n"
        f"- **Collector:** tech-stack-collector v{VERSION}\n"
        f"- **Mode:** {'full (sensitive)' if full else 'safe'}\n"
    )
    emit(header)

    collectors = [
        lambda: collect_system(include_sensitive=full),
        lambda: collect_docker(safe=not full),
        collect_languages,
        lambda: collect_package_managers(include_details=full),
        lambda: collect_services(safe=not full),
        collect_databases,
        lambda: collect_web_servers(include_sites=full),
        collect_devops,
        collect_cli_tools,
        collect_network_security,
        collect_virtualization,
        collect_monitoring,
    ]
    if full:
        collectors.extend([
            collect_key_dirs,
            collect_ports,
            collect_git_repos,
            collect_cron,
            collect_shell_env,
        ])

    # Run all collectors in parallel
    section_map: dict[str, str] = {}
    with ThreadPoolExecutor(max_workers=6) as pool:
        futs = {pool.submit(fn): fn.__name__ for fn in collectors}
        for f in as_completed(futs):
            try:
                title, content = f.result()
                if content:
                    section_map[title] = content
            except Exception as exc:
                section_map[futs[f]] = f"_Error: {exc}_"

    # Assemble in defined order, streaming each section
    body_parts: list[str] = []
    for title in SECTION_ORDER:
        if title in section_map:
            sec = f"\n## {title}\n\n{section_map[title]}\n"
            body_parts.append(sec)
            emit(sec)
    # Any extra sections not in predefined order
    for title, content in section_map.items():
        if title not in SECTION_ORDER and content:
            sec = f"\n## {title}\n\n{content}\n"
            body_parts.append(sec)
            emit(sec)

    # ── Tag extraction from structured data ─────────────────────────────
    tags = TagStore()
    _extract_tags_from_sections(tags, section_map)

    tag_sec = ""
    formatted = tags.format_tags()
    if formatted:
        tag_sec = f"\n---\n\n## Technology Profile\n\n{formatted}\n"
        emit(tag_sec)

    report = header + "\n".join(body_parts) + tag_sec

    # Save to file
    ts_file = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    if full:
        safe_host = re.sub(r'[^\w\-.]', '_', hostname)
        filename = f"techstack_{safe_host}_{ts_file}.md"
    else:
        filename = f"techstack_safe_{ts_file}.md"
    filepath = os.path.join(output_dir, filename)
    try:
        os.makedirs(output_dir, exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(report)
        os.chmod(filepath, 0o600)
        os.chmod(output_dir, 0o700)
        emit(f"\n---\n✅ Report saved → {os.path.abspath(filepath)}")
    except OSError as exc:
        print(f"\n⚠️  Save failed: {exc}", file=sys.stderr)

    return report


def _extract_tags_from_sections(tags: TagStore, sections: dict[str, str]) -> None:
    """Feed structured section data into TagStore for intelligent tagging."""

    # 1. Docker images — safe mode contains only canonical category/name rows;
    # full mode contains raw image identifiers.
    docker_sec = sections.get("Docker / Containers", "")
    if docker_sec:
        for row in md_table_rows(docker_sec):
            if len(row) >= 2 and row[0] in {category for category, _ in TagStore._CAT_ORDER}:
                tags.add(row[0], row[1])
        # Extract image names from table rows and compose output
        for m in re.finditer(r'(?:^|\|)\s*(\S+/\S+:\S+|\w[\w.-]+:\w[\w.-]+)', docker_sec, re.M):
            tags.resolve_docker_image(m.group(1))
        # Also catch compose project names for context
        for m in re.finditer(r'^(\w[\w-]+)\s+running', docker_sec, re.M):
            proj = m.group(1).lower()
            _COMPOSE_MAP = {
                "dify": ("Applications", "Dify (AI/LLM)"),
                "docker": None,  # generic, skip
                "erpnext": ("Applications", "ERPNext"),
                "overleaf": ("Applications", "Overleaf (LaTeX)"),
                "opensign": ("Applications", "OpenSign"),
                "aria2": ("Applications", "Aria2 (Downloader)"),
                "emqx": ("MessageBrokers", "EMQX (MQTT)"),
                "openresty": ("ReverseProxy", "OpenResty (Nginx)"),
            }
            for key, val in _COMPOSE_MAP.items():
                if key in proj and val:
                    tags.add(val[0], val[1])

    # 2. Running services
    svc_sec = sections.get("Running Services", "")
    for line in svc_sec.split("\n"):
        line = line.strip().lstrip("- ")
        if line and not line.startswith("_") and not line.startswith("#"):
            tags.resolve_service(line)

    # 3. Programming languages — from table rows
    lang_sec = sections.get("Programming Languages", "")
    for row in md_table_rows(lang_sec):
        if row and row[0]:
            tags.resolve_tool(row[0], "Languages")

    # 4. DevOps tools
    devops_sec = sections.get("Cloud & DevOps Tools", "")
    for row in md_table_rows(devops_sec):
        if row and row[0]:
            tags.resolve_tool(row[0], "DevOps")

    # 5. Databases (installed, not just Docker)
    db_sec = sections.get("Databases", "")
    for row in md_table_rows(db_sec):
        if row and row[0]:
            tags.resolve_tool(row[0], "Databases")

    # 6. Web servers
    web_sec = sections.get("Web Servers", "")
    for m in re.finditer(r'\*\*(\w[\w.]*)\*\*', web_sec):
        tags.resolve_tool(m.group(1), "ReverseProxy")

    # 7. CLI tools — selective: skip trivial utils, keep skill-indicative ones
    cli_sec = sections.get("CLI & Utility Tools", "")
    _CLI_SKILL_SET = {
        "git", "tmux", "neovim", "vim", "jq", "yq", "fzf", "ripgrep",
        "fd", "bat", "ffmpeg", "imagemagick", "pandoc", "rsync",
        "btop", "htop", "strace", "lsof",
    }
    for row in md_table_rows(cli_sec):
        name = row[0].strip() if row else ""
        if name.lower() in _CLI_SKILL_SET:
            tags.resolve_tool(name, "CLI")

    # 8. Network & Security
    net_sec = sections.get("Network & Security", "")
    for m in re.finditer(r'\*\*(\w[\w.]*)\*\*', net_sec):
        tags.resolve_tool(m.group(1), "Security")

    # 9. Monitoring
    mon_sec = sections.get("Monitoring & Observability", "")
    for m in re.finditer(r'\*\*(\w[\w. ]*)\*\*', mon_sec):
        tags.resolve_tool(m.group(1), "Monitoring")

    # 10. Virtualization
    virt_sec = sections.get("Virtualization", "")
    if "kvm" in virt_sec.lower() or "qemu" in virt_sec.lower():
        tags.add("Virtualization", "KVM/QEMU")
    for m in re.finditer(r'\*\*(\w[\w./]*)\*\*', virt_sec):
        name = m.group(1)
        if name.lower() not in ("platform",):
            tags.resolve_tool(name, "Virtualization")

    # 11. Git repositories
    git_sec = sections.get("Git Repositories", "")
    for m in re.finditer(r'\|\s*(https?://\S+)\s*\|', git_sec):
        tags.resolve_git_repo(m.group(1))

    # 12. Key directories — detect notable software in /opt
    key_sec = sections.get("Key Directories", "")
    _DIR_MAP = {
        "1panel":    ("Applications", "1Panel"),
        "dify":      ("Applications", "Dify (AI/LLM)"),
        "overleaf":  ("Applications", "Overleaf (LaTeX)"),
        "smarthome": ("Applications", "IoT/Smart Home"),
        "nezha":     ("Monitoring",   "Nezha (Probe)"),
        "aria2":     ("Applications", "Aria2 (Downloader)"),
    }
    for line in key_sec.split("\n"):
        low = line.strip().lstrip("- ").lower()
        for key, (cat, tag) in _DIR_MAP.items():
            if key in low:
                tags.add(cat, tag)

    # 13. Shell env — detect dev tools from env vars
    shell_sec = sections.get("Shell Environment", "")
    if "GOPATH" in shell_sec or "GOROOT" in shell_sec:
        tags.add("Languages", "Go")
    if "JAVA_HOME" in shell_sec:
        tags.add("Languages", "Java")
    if "NVM_DIR" in shell_sec:
        tags.add("Languages", "Node.js")
    if "PYENV_ROOT" in shell_sec:
        tags.add("Languages", "Python")
    if "CARGO_HOME" in shell_sec:
        tags.add("Languages", "Rust")
    if "CONDA" in shell_sec:
        tags.add("Languages", "Python (Conda)")

    # 14. Package managers context
    pkg_sec = sections.get("Package Managers", "")
    if "### pip" in pkg_sec:
        tags.add("Languages", "Python")
    if "### npm" in pkg_sec:
        tags.add("Languages", "Node.js")
    if "### cargo" in pkg_sec:
        tags.add("Languages", "Rust")
    if "### Go binaries" in pkg_sec:
        tags.add("Languages", "Go")
    if "### gem" in pkg_sec:
        tags.add("Languages", "Ruby")
    if "### composer" in pkg_sec:
        tags.add("Languages", "PHP")
    if "### snap" in pkg_sec:
        tags.add("DevOps", "Snap")


# ── CLI ─────────────────────────────────────────────────────────────────────
def main() -> None:
    script_dir = os.path.dirname(os.path.abspath(__file__))
    default_reports = os.path.join(script_dir, "reports")
    parser = argparse.ArgumentParser(
        description="Collect server tech stack for CV/resume building.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python3 collector.py\n"
            "  python3 collector.py --output-dir /tmp/reports\n"
            "  python3 remote_runner.py -c targets.yaml\n"
        ),
    )
    parser.add_argument(
        "--output-dir", "-o", default=default_reports,
        help=f"Directory to save the report file (default: {default_reports})",
    )
    parser.add_argument(
        "--full", action="store_true",
        help="Include sensitive host, topology, path, Git, cron, and environment data",
    )
    try:
        args = parser.parse_args()
    except SystemExit:
        args = argparse.Namespace(output_dir=default_reports, full=False)

    if args.full:
        print(
            "WARNING: --full may expose hostnames, internal paths, ports, Git remotes, "
            "scheduled commands, and environment metadata.",
            file=sys.stderr,
        )
    build_report(output_dir=args.output_dir, full=args.full)


if __name__ == "__main__":
    main()
