#!/usr/bin/env bash
set -euo pipefail

ROOT=/home/mohd/NL_Swarm
PYTHON=/home/mohd/NL_Swarm/.venv/bin/python
SESSION=coordinator

if tmux has-session -t "$SESSION" 2>/dev/null; then
  echo "$SESSION already running"
  exit 0
fi

tmux new-session -d -s "$SESSION" "$PYTHON -u $ROOT/nl_coverage_coordinator.py"
echo "started $SESSION"
