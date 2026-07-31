#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────
# tech-stack-collector — reviewed local execution wrapper
#
# Run this wrapper from a reviewed local checkout. It deliberately does not
# download or pipe remote code into an interpreter. Safe mode is the default;
# pass --full only for sensitive private inventory.
# ─────────────────────────────────────────────────────────────
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
COLLECTOR="$SCRIPT_DIR/collector.py"

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
if [[ " $* " == *" --full "* ]]; then
    echo "⚠️  Full mode may expose hostnames, ports, paths, Git remotes, cron, and environment data." >&2
else
    echo "🔒 Safe privacy mode"
fi
echo ""

# Run the reviewed local copy.
if [ ! -f "$COLLECTOR" ]; then
    echo "❌ collector.py not found next to run.sh" >&2
    echo "   Clone the repository, review it, and run this wrapper from the checkout." >&2
    exit 1
fi
exec "$PY" "$COLLECTOR" "$@"
