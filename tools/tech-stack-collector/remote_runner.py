#!/usr/bin/env python3
"""
remote_runner.py — Run tech-stack-collector on remote servers via SSH.

Supports two authentication methods:
  • SSH key  (recommended)
  • Password (requires paramiko)

Three ways to specify targets:
  1. Config file:   python3 remote_runner.py -c targets.yaml
  2. Single host:   python3 remote_runner.py -H 192.0.2.10 -u root -k ~/.ssh/id_ed25519
  3. Inline pass:   python3 remote_runner.py -H 192.0.2.10 -u root -p

Output: Streamed to terminal + saved per-host in ./reports/

Dependencies: paramiko, pyyaml (optional, for YAML configs)
  pip install paramiko pyyaml
"""

from __future__ import annotations

import argparse
import datetime
import getpass
import json
import os
import re
import sys
import textwrap
from pathlib import Path
from typing import Any

try:
    import paramiko
except ImportError:
    print(
        "ERROR: paramiko is required for SSH remote execution.\n"
        "       pip install paramiko",
        file=sys.stderr,
    )
    sys.exit(1)

# ── Globals ─────────────────────────────────────────────────────────────────
SCRIPT_DIR = Path(__file__).resolve().parent
COLLECTOR_PATH = SCRIPT_DIR / "collector.py"
REPORTS_DIR = SCRIPT_DIR / "reports"
CONNECT_TIMEOUT = 15  # seconds
EXEC_TIMEOUT = 120    # seconds — some commands are slow
VERSION_PATTERN = re.compile(r'^VERSION\s*=\s*["\']([^"\']+)["\']', re.MULTILINE)


# ── Config Loader ───────────────────────────────────────────────────────────
def load_config(path: str) -> list[dict[str, Any]]:
    """Load target list from YAML or JSON config file."""
    p = Path(path)
    text = p.read_text(encoding="utf-8")

    if p.suffix in (".yaml", ".yml"):
        try:
            import yaml
            data = yaml.safe_load(text)
        except ImportError:
            print(
                "WARNING: pyyaml not installed, attempting basic YAML parse.\n"
                "         For full YAML support: pip install pyyaml",
                file=sys.stderr,
            )
            data = _basic_yaml_parse(text)
    else:
        data = json.loads(text)

    targets = data if isinstance(data, list) else data.get("targets", [data])
    # Validate
    for i, t in enumerate(targets):
        if "host" not in t:
            raise ValueError(f"Target #{i} missing 'host'")
        t.setdefault("port", 22)
        t.setdefault("user", "root")
        t.setdefault("auth", "key")
        t.setdefault("name", t["host"])
        if t["auth"] == "key":
            t.setdefault("key_path", str(Path.home() / ".ssh" / "id_rsa"))
    return targets


def _basic_yaml_parse(text: str) -> dict:
    """Minimal YAML-subset parser for simple key-value structures."""
    # Only handles the flat targets list structure we need
    import re
    targets: list[dict] = []
    current: dict[str, Any] = {}
    for line in text.split("\n"):
        line = line.rstrip()
        if not line or line.lstrip().startswith("#"):
            continue
        # New list item
        m = re.match(r"\s*-\s+(\w+):\s*(.*)", line)
        if m:
            if current:
                targets.append(current)
            current = {m.group(1): _yaml_val(m.group(2))}
            continue
        # Continuation key
        m = re.match(r"\s+(\w+):\s*(.*)", line)
        if m:
            current[m.group(1)] = _yaml_val(m.group(2))
    if current:
        targets.append(current)
    return {"targets": targets}


def _yaml_val(s: str) -> Any:
    s = s.strip().strip('"').strip("'")
    if s.lower() in {"true", "false"}:
        return s.lower() == "true"
    if s.isdigit():
        return int(s)
    return s


# ── SSH Execution ───────────────────────────────────────────────────────────
def run_on_target(
    target: dict[str, Any],
    collector_code: str,
    full: bool = False,
    display_name: str | None = None,
) -> str:
    """SSH into target, execute collector, stream output, return full text."""
    name = target["name"]
    host = target["host"]
    port = int(target["port"])
    user = target["user"]
    auth = target["auth"]
    strict_host_key = target.get("strict_host_key", True)

    label = display_name or (name if full else "target")
    endpoint = f" ({user}@{host}:{port})" if full else ""
    banner = f"{'='*60}\n  📡 {label}{endpoint}\n{'='*60}"
    print(banner, flush=True)

    client = paramiko.SSHClient()
    client.load_system_host_keys()
    if strict_host_key:
        client.set_missing_host_key_policy(paramiko.RejectPolicy())
    else:
        print("  WARNING: accepting an unknown SSH host key without verification", flush=True)
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    connect_kwargs: dict[str, Any] = {
        "hostname": host,
        "port": port,
        "username": user,
        "timeout": CONNECT_TIMEOUT,
        "allow_agent": True,
        "look_for_keys": True,
    }

    if auth == "password":
        pw = target.get("password")
        if not pw:
            pw = getpass.getpass(f"  Password for {user}@{host}: ")
        connect_kwargs["password"] = pw
        connect_kwargs["look_for_keys"] = False
        connect_kwargs["allow_agent"] = False
    elif auth == "key":
        key_path = os.path.expanduser(target.get("key_path", "~/.ssh/id_rsa"))
        passphrase = target.get("key_passphrase")
        if passphrase:
            connect_kwargs["key_filename"] = key_path
            connect_kwargs["passphrase"] = passphrase
        else:
            connect_kwargs["key_filename"] = key_path

    try:
        client.connect(**connect_kwargs)
    except Exception as exc:
        detail = str(exc) if full else "details hidden in safe mode"
        msg = f"  ❌ Connection failed: {detail}"
        print(msg, flush=True)
        return msg

    # Pipe collector.py through stdin → python3 -
    # This avoids needing to upload a file
    try:
        transport = client.get_transport()
        if transport is None:
            return "  ❌ Transport not available"
        channel = transport.open_session()
        channel.settimeout(EXEC_TIMEOUT)
        collector_args = " --full" if full else ""
        channel.exec_command(f"python3 - --output-dir /tmp{collector_args}")

        # Send collector code through stdin
        channel.sendall(collector_code.encode("utf-8"))
        channel.shutdown_write()

        # Stream stdout line by line
        output_lines: list[str] = []
        buf = b""
        while True:
            if channel.recv_ready():
                chunk = channel.recv(4096)
                if not chunk:
                    break
                buf += chunk
                while b"\n" in buf:
                    line, buf = buf.split(b"\n", 1)
                    decoded = line.decode("utf-8", errors="replace")
                    output_lines.append(decoded)
                    print(decoded, flush=True)
            elif channel.exit_status_ready():
                # Drain remaining
                while channel.recv_ready():
                    chunk = channel.recv(4096)
                    buf += chunk
                break

        # Flush remaining buffer
        if buf:
            decoded = buf.decode("utf-8", errors="replace")
            output_lines.append(decoded)
            print(decoded, flush=True)

        exit_code = channel.recv_exit_status()
        if exit_code != 0:
            # Read stderr
            stderr = b""
            while channel.recv_stderr_ready():
                stderr += channel.recv_stderr(4096)
            if stderr:
                err_msg = stderr.decode("utf-8", errors="replace")
                print(f"\n⚠️  stderr: {err_msg}", flush=True)
                output_lines.append(f"\n⚠️  stderr: {err_msg}")

        channel.close()
        return "\n".join(output_lines)

    except Exception as exc:
        detail = str(exc) if full else "details hidden in safe mode"
        msg = f"  ❌ Execution error: {detail}"
        print(msg, flush=True)
        return msg
    finally:
        client.close()


def save_report(name: str, content: str, run_dir: Path) -> Path:
    """Save report into the run directory with a clean name."""
    safe_name = "".join(c if c.isalnum() or c in "-_." else "_" for c in name)
    filepath = run_dir / f"{safe_name}.md"
    filepath.write_text(content, encoding="utf-8")
    os.chmod(filepath, 0o600)
    return filepath


def collector_version(collector_code: str) -> str:
    """Read the collector version without importing or executing remote code."""
    match = VERSION_PATTERN.search(collector_code)
    return match.group(1) if match else "unknown"


def write_index(
    run_dir: Path,
    results: list[tuple[str, str, Path]],
    ts: str,
    version: str,
) -> Path:
    """Write _index.md summary for this collection run."""
    lines = [
        f"# Collection Run — {ts}",
        "",
        f"**Targets:** {len(results)}  ",
        f"**Success:** {sum(1 for _, s, _ in results if s == 'ok')}  ",
        f"**Failed:** {sum(1 for _, s, _ in results if s != 'ok')}",
        "",
        "| # | Server | Status | Report |",
        "| --- | --- | --- | --- |",
    ]
    for i, (name, status, path) in enumerate(results, 1):
        link = f"[{path.name}](./{path.name})" if status == "ok" else "—"
        icon = "✅" if status == "ok" else "❌"
        lines.append(f"| {i} | {name} | {icon} {status} | {link} |")

    lines.extend(["", "---", f"_Generated by tech-stack-collector v{version}_"])
    index_path = run_dir / "_index.md"
    index_path.write_text("\n".join(lines), encoding="utf-8")
    os.chmod(index_path, 0o600)
    return index_path


# ── CLI ─────────────────────────────────────────────────────────────────────
def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run tech-stack-collector on remote servers via SSH.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""\
            Examples:
              # Run on a single host with SSH key
              python3 remote_runner.py -H 192.0.2.10 -u root -k ~/.ssh/id_ed25519

              # Run on a single host with password
              python3 remote_runner.py -H 192.0.2.10 -u root -p

              # Run on multiple hosts from config
              python3 remote_runner.py -c targets.yaml

              # Custom output directory
              python3 remote_runner.py -c targets.yaml -o /tmp/reports
        """),
    )

    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument(
        "-c", "--config", metavar="FILE",
        help="Path to targets config file (YAML or JSON)",
    )
    mode.add_argument(
        "-H", "--host", metavar="ADDR",
        help="Single target host address",
    )

    parser.add_argument("-P", "--port", type=int, default=22, help="SSH port (default: 22)")
    parser.add_argument("-u", "--user", default="root", help="SSH user (default: root)")

    auth = parser.add_mutually_exclusive_group()
    auth.add_argument("-k", "--key", metavar="PATH", help="SSH private key path")
    auth.add_argument("-p", "--password", action="store_true", help="Use password auth (will prompt)")

    parser.add_argument(
        "-o", "--output-dir", default=str(REPORTS_DIR),
        help=f"Directory to save reports (default: {REPORTS_DIR})",
    )
    parser.add_argument(
        "--collector", metavar="PATH",
        help=f"Path to collector.py (default: {COLLECTOR_PATH})",
    )
    parser.add_argument(
        "--full", action="store_true",
        help="Request the collector's sensitive full-inventory mode",
    )
    parser.add_argument(
        "--insecure-auto-add-host-key",
        action="store_true",
        help="Accept unknown SSH host keys without verification (unsafe)",
    )

    args = parser.parse_args()

    # Load collector script
    collector_path = Path(args.collector) if args.collector else COLLECTOR_PATH
    if not collector_path.exists():
        print(f"ERROR: collector.py not found at {collector_path}", file=sys.stderr)
        sys.exit(1)
    collector_code = collector_path.read_text(encoding="utf-8")

    # Build target list
    if args.config:
        targets = load_config(args.config)
    else:
        target: dict[str, Any] = {
            "name": args.host,
            "host": args.host,
            "port": args.port,
            "user": args.user,
            "strict_host_key": not args.insecure_auto_add_host_key,
        }
        if args.password:
            target["auth"] = "password"
        else:
            target["auth"] = "key"
            target["key_path"] = args.key or str(Path.home() / ".ssh" / "id_rsa")
        targets = [target]

    output_base = Path(args.output_dir)

    # Create timestamped run directory
    run_ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    report_names = [
        str(target["name"]) if args.full else f"target-{index:02d}"
        for index, target in enumerate(targets, 1)
    ]
    if len(targets) == 1:
        safe = "".join(c if c.isalnum() or c in "-_." else "_" for c in report_names[0])
        run_dir = output_base / f"run_{run_ts}_{safe}"
    else:
        run_dir = output_base / f"run_{run_ts}"
    run_dir.mkdir(parents=True, exist_ok=True)
    os.chmod(run_dir, 0o700)

    print(f"\n🚀 Running tech-stack-collector on {len(targets)} target(s)")
    print(f"📂 Output → {run_dir}\n", flush=True)

    # Execute on each target sequentially (streaming requires sequential)
    results: list[tuple[str, str, Path]] = []
    for target, report_name in zip(targets, report_names):
        report_text = run_on_target(
            target,
            collector_code,
            full=args.full,
            display_name=report_name,
        )
        is_fail = report_text.strip().startswith("❌") or "Connection failed" in report_text
        status = "failed" if is_fail else "ok"
        filepath = save_report(report_name, report_text, run_dir)
        results.append((report_name, status, filepath))
        print(f"\n💾 Saved → {filepath}\n", flush=True)

    # Write index
    index_path = write_index(run_dir, results, run_ts, collector_version(collector_code))

    # Summary
    ok = sum(1 for _, s, _ in results if s == "ok")
    fail = len(results) - ok
    print("\n" + "=" * 60)
    print(f"  📋 Summary — {ok} ok, {fail} failed")
    print(f"  📂 {run_dir}")
    print("=" * 60)
    for name, status, path in results:
        icon = "✅" if status == "ok" else "❌"
        print(f"  {icon} {name:30s} → {path.name}")
    print(f"\n  📄 Index → {index_path}")
    print()


if __name__ == "__main__":
    main()
