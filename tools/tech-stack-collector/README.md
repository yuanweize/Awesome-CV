# 🔍 tech-stack-collector

> Collect server technical stack information for CV / resume building.
> Run on your VPS, get an AI-friendly Markdown report of your tech skills.

## Quick Start

### Mode 1: One-liner remote execution (on any Debian/Ubuntu server)

```bash
# curl
curl -fsSL https://raw.githubusercontent.com/yuanweize/Awesome-CV/main/tools/tech-stack-collector/collector.py | python3

# wget
wget -qO- https://raw.githubusercontent.com/yuanweize/Awesome-CV/main/tools/tech-stack-collector/collector.py | python3

# or via bash wrapper (auto-detects python3, curl/wget)
curl -fsSL https://raw.githubusercontent.com/yuanweize/Awesome-CV/main/tools/tech-stack-collector/run.sh | bash
```

### Mode 2: Local execution

```bash
python3 collector.py
python3 collector.py --output-dir /tmp/reports
```

### Mode 3: SSH remote execution (from your local machine)

```bash
# Install dependencies first
pip install paramiko pyyaml

# Single host (SSH key)
python3 remote_runner.py -H 10.0.0.1 -u root -k ~/.ssh/id_ed25519

# Single host (password — will prompt)
python3 remote_runner.py -H 10.0.0.1 -u root -p

# Multiple hosts from config file
cp targets.example.yaml targets.yaml   # edit with your servers
python3 remote_runner.py -c targets.yaml

# Custom output directory
python3 remote_runner.py -c targets.yaml -o ~/my-reports
```

## What It Collects

| Category                  | Details                                              |
|---------------------------|------------------------------------------------------|
| **System**                | OS, kernel, arch, CPU, memory, disk, uptime          |
| **Docker / Containers**   | Running containers, images, compose, volumes, nets   |
| **Programming Languages** | Python, Node, Java, Go, Rust, Ruby, PHP, .NET, etc.  |
| **Package Managers**      | pip, npm, cargo, gem, go, snap, composer              |
| **Key Directories**       | /opt, /usr/local/bin, /srv, /var/www, ~/projects      |
| **Running Services**      | systemd services (filtered: notable vs system)       |
| **Listening Ports**       | All TCP listeners with process names                 |
| **Databases**             | PostgreSQL, MySQL, Redis, MongoDB, SQLite, etc.       |
| **Web Servers**           | Nginx, Apache, Caddy, Traefik, HAProxy               |
| **Cloud & DevOps**        | Terraform, Ansible, kubectl, Helm, AWS/Azure/GCP CLI  |
| **CLI Tools**             | git, tmux, vim, jq, ripgrep, ffmpeg, etc.             |
| **Network & Security**    | WireGuard, iptables, UFW, Certbot, Fail2ban           |
| **Git Repos**             | Found repos with remotes and branches                |
| **Scheduled Tasks**       | Crontab, /etc/cron.d, systemd timers                 |
| **Virtualization**        | KVM, QEMU, LXC, LXD, platform type                  |
| **Monitoring**            | Prometheus, Grafana, Telegraf, Netdata                |
| **Shell Environment**     | Shell, env vars, aliases, SSH keys                   |

## Output Format

Structured Markdown with tables and bullet lists — optimized for AI consumption.
Each report ends with a **Technology Profile** section — categorized tags generated
by a knowledge-base algorithm (130+ Docker image mappings, service/repo resolution).

```markdown
## Technology Profile

**🐳 Containers & Orchestration**
`Docker`, `containerd`

**🗄️ Databases**
`MariaDB`, `MongoDB`, `PostgreSQL`, `Weaviate (Vector DB)`

**📦 Self-Hosted Applications**
`Dify (AI/LLM)`, `ERPNext`, `Overleaf (LaTeX)`, `OpenSign`

**🔨 CLI Tooling**
`FFmpeg`, `Git`, `Vim`, `jq`, `tmux`

---
**All (43):** `1Panel`, `Caddy`, `Dify (AI/LLM)`, `Docker`, ...
```

## File Structure

```
tech-stack-collector/
├── collector.py              # Main script (stdlib only, zero deps)
├── remote_runner.py          # SSH batch execution via SSH
├── run.sh                    # Bash wrapper for curl|bash
├── targets.example.yaml      # Config template (YAML)
├── targets.example.json      # Config template (JSON)
├── requirements.txt          # Deps for remote mode only
├── .gitignore                # Ignores reports/, targets.yaml, etc.
├── reports/                  # Output directory (gitignored)
│   └── run_20260210_132618/  # Timestamped run folder
│       ├── _index.md         # Summary table of this run
│       ├── Server_A.md       # Per-host report
│       ├── Server_B.md
│       └── ...
└── README.md
```

## Design Principles

- **collector.py** uses **only Python stdlib** — safe for `curl | python3`
- **Parallel execution** — commands run concurrently via `ThreadPoolExecutor`
- **Graceful degradation** — missing commands are silently skipped
- **Streaming output** — lines flush immediately for real-time feedback
- **AI-friendly** — Markdown tables, clear sections, categorized technology profile
- **Smart tagging** — 130+ Docker image mappings, service/repo resolution, 13 categories
- **Dual output** — always prints to stdout AND saves to local file
- **Organized reports** — timestamped run folders with `_index.md` summary

## Output Files

**Local mode** — saved in cwd with timestamped filenames:

```
techstack_myserver_20260210_143052.md
```

**Remote mode** — each run creates a timestamped folder under `reports/`:

```
reports/
└── run_20260210_132618/     # one folder per batch run
    ├── _index.md            # summary: success/fail table
    ├── Server_A.md          # clean name per host
    ├── Server_B.md
    └── ...
```

## Workflow

1. Run `collector.py` on each of your VPS servers
2. Collect the generated `.md` files
3. Feed them to your AI agent for tech stack analysis
4. AI summarizes your skills and updates your CV sections
