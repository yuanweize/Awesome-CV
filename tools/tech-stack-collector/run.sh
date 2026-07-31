#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────
# tech-stack-collector  —  one-liner remote execution wrapper
#
# Usage (pick one):
#   curl -fsSL https://raw.githubusercontent.com/yuanweize/Awesome-CV/main/tools/tech-stack-collector/run.sh | bash
#   wget -qO- https://raw.githubusercontent.com/yuanweize/Awesome-CV/main/tools/tech-stack-collector/run.sh | bash
#
# Or directly run the Python script:
#   curl -fsSL https://raw.githubusercontent.com/yuanweize/Awesome-CV/main/tools/tech-stack-collector/collector.py | python3
# Safe mode is the default. Pass --full only for sensitive private inventory.
# ─────────────────────────────────────────────────────────────
set -euo pipefail

REPO_BASE="https://raw.githubusercontent.com/yuanweize/Awesome-CV/main/tools/tech-stack-collector"
SCRIPT_URL="${REPO_BASE}/collector.py"

# Find python3
PY=""
for bin in python3 python; do
    if command -v "$bin" &>/dev/null; then
        ver=$("$bin" -c "import sys; print(sys.version_info.major)" 2>/dev/null || echo 0)
        if [ "$ver" = "3" ]; then
            PY="$bin"
            break
        fi
    fi
done

if [ -z "$PY" ]; then
    echo "❌ Python 3 is required but not found." >&2
    echo "   Install: apt install python3  or  yum install python3" >&2
    exit 1
fi

echo "🔍 Using $PY ($($PY --version 2>&1))"
echo "📥 Fetching collector from GitHub..."
if [[ " $* " == *" --full "* ]]; then
    echo "⚠️  Full mode may expose hostnames, ports, paths, Git remotes, cron, and environment data." >&2
else
    echo "🔒 Safe privacy mode"
fi
echo ""

# Download & run
if command -v curl &>/dev/null; then
    curl -fsSL "$SCRIPT_URL" | "$PY" - "$@"
elif command -v wget &>/dev/null; then
    wget -qO- "$SCRIPT_URL" | "$PY" - "$@"
else
    echo "❌ curl or wget required" >&2
    exit 1
fi
