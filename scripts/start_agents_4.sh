#!/usr/bin/env bash
set -euo pipefail

ROOT=/home/mohd/NL_Swarm
PYTHON=/home/mohd/NL_Swarm/.venv/bin/python

start_one() {
  local name="$1"
  local script="$2"
  if tmux has-session -t "$name" 2>/dev/null; then
    echo "$name already running"
    return 0
  fi
  tmux new-session -d -s "$name" "$PYTHON -u $ROOT/$script"
  echo "started $name"
}

start_one agent_uav1 D1_agent_new.py
start_one agent_uav2 D2_agent_new.py
start_one agent_uav3 D3_agent_new.py
start_one agent_uav4 D4_agent_new.py
