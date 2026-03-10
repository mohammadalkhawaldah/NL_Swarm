#!/usr/bin/env bash
set -euo pipefail

ROOT=/home/mohd/NL_Swarm
PYTHON=/home/mohd/NL_Swarm/.venv/bin/python

if tmux has-session -t operator 2>/dev/null; then
  echo "operator already running"
  exit 0
fi

tmux new-session -d -s operator "$PYTHON -u $ROOT/task_extract_send_rdp.py"
echo "started operator"
