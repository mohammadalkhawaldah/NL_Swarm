#!/usr/bin/env bash
set -euo pipefail

ROOT=/home/mohd/NL_Swarm
RUN_DIR="$ROOT/run"

for session in operator coordinator agent_uav1 agent_uav2 agent_uav3 agent_uav4 mavsdk_uav1 mavsdk_uav2 mavsdk_uav3 mavsdk_uav4 sitl_uav1 sitl_uav2 sitl_uav3 sitl_uav4; do
  if tmux has-session -t "$session" 2>/dev/null; then
    tmux kill-session -t "$session"
    echo "stopped tmux session $session"
  fi
done

pkill -f '/home/mohd/bin/mavsdk_server -p 5004[0-3]' 2>/dev/null || true
pkill -f 'D[1-4]_agent_new.py' 2>/dev/null || true
pkill -f 'nl_coverage_coordinator.py' 2>/dev/null || true
pkill -f 'task_extract_send_rdp.py' 2>/dev/null || true

if [[ ! -d "$RUN_DIR" ]]; then
  exit 0
fi

for pidfile in "$RUN_DIR"/*.pid; do
  [[ -e "$pidfile" ]] || continue
  pid=$(cat "$pidfile")
  name=$(basename "$pidfile" .pid)
  if [[ -n "$pid" ]] && kill -0 "$pid" 2>/dev/null; then
    kill "$pid" 2>/dev/null || true
    echo "stopped $name pid=$pid"
  else
    echo "stale pid for $name pid=$pid"
  fi
  rm -f "$pidfile"
done
