# tech-stack-collector

Inventory technologies that are actually installed on a Linux host, then use the
result as private evidence while maintaining an evidence-first master CV.

The collector does **not** prove professional proficiency. Installed software is
only a discovery aid; a CV claim still needs scope, personal ownership, evidence,
and enough interview depth.

## Privacy modes

Safe mode is the default in v2. It redacts the hostname and user, strips private
registry paths from image names, and omits the most sensitive collectors:

- listening ports and bind addresses;
- Git repository paths and remotes;
- key directories and project names;
- crontab and systemd timer commands;
- shell environment data;
- container names, Compose project names, volumes, and networks;
- enabled web-site names.

`--full` restores those sections. A full report is sensitive infrastructure
documentation. Do not upload it to an AI service, attach it to an application,
or commit it to Git without manual redaction.

默认是安全模式。`--full` 会包含主机名、端口、路径、Git remote、定时任务和
环境信息，只能在明确了解风险时使用；完整报告不能直接上传给 AI 或提交到仓库。

## Run locally

```bash
# Safe mode
python3 collector.py
python3 collector.py --output-dir /tmp/reports

# Sensitive full inventory — opt in explicitly
python3 collector.py --full --output-dir /tmp/private-reports
```

## One-line execution

Review remote code before piping it into an interpreter. The command below runs
safe mode:

```bash
curl -fsSL https://raw.githubusercontent.com/yuanweize/Awesome-CV/main/tools/tech-stack-collector/collector.py | python3
```

Pass `--full` only when required:

```bash
curl -fsSL https://raw.githubusercontent.com/yuanweize/Awesome-CV/main/tools/tech-stack-collector/collector.py | python3 - --full
```

## Run over SSH

```bash
python3 -m pip install -r requirements.txt

# Safe mode, one host
python3 remote_runner.py -H 192.0.2.10 -u root -k ~/.ssh/id_ed25519

# Safe mode, multiple hosts
cp targets.example.yaml targets.yaml
python3 remote_runner.py -c targets.yaml

# Sensitive full inventory
python3 remote_runner.py -c targets.yaml --full
```

The example addresses are RFC 5737 documentation networks. Replace them only in
the ignored `targets.yaml` or `targets.json`; never edit the tracked examples with
real infrastructure details. Password authentication prompts interactively when
the password field is omitted. Unknown SSH host keys are rejected by default; add
the real host key to `known_hosts` after verifying its fingerprint. The
`--insecure-auto-add-host-key` escape hatch weakens MITM protection and should be
used only in a controlled, disposable environment.

## Safe-mode output

Safe mode can include:

| Category | Examples |
|---|---|
| System | OS, kernel, architecture, CPU, memory, disk |
| Container images | Image basename and size, without registry path |
| Languages | Python, Go, Rust, Java, C/C++ toolchain |
| Package managers | pip/npm/cargo summaries |
| Services | Notable systemd service names |
| Data stores | PostgreSQL, Redis, SQLite, InfluxDB |
| Web servers | Nginx, Caddy, Apache versions |
| DevOps tools | Terraform, Ansible, kubectl, Helm |
| Security | WireGuard, nftables, Certbot, Fail2ban |
| Monitoring | Prometheus, Grafana, Telegraf |
| Virtualisation | KVM/QEMU, libvirt, LXC |

Each report ends with a categorized `Technology Profile`. Treat it as an
inventory, not a ready-made Skills section.

## Evidence-first workflow

1. Run safe mode and keep the report under the ignored `reports/` directory.
2. Manually select technology usage that you can explain and demonstrate.
3. Create an evidence record in `meta/master_cv.yaml`; never paste the raw report.
4. Write an atomic claim with the correct scope (`personal`, `academic`, or work).
5. Run `make validate` before exporting a JD context.
6. Use `./cv context --jd job.md --role systems` to expose only eligible claims.

## Files

```text
tools/tech-stack-collector/
├── collector.py
├── remote_runner.py
├── run.sh
├── requirements.txt
├── targets.example.yaml
├── targets.example.json
└── reports/                 # ignored except .gitkeep
```

Runtime reports, target files, passwords, key paths, hostnames, and internal IPs
must remain private. Run `./cv privacy-check` before every push.
