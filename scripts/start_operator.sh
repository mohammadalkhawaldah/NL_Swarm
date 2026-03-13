#!/usr/bin/env bash
set -euo pipefail

ROOT=/home/mohd/NL_Swarm
LOG_DIR="$ROOT/logs"
RUN_DIR="$ROOT/run"
PYTHON="$ROOT/.venv/bin/python"
LOG="$LOG_DIR/operator.log"
PIDFILE="$RUN_DIR/operator.pid"

mkdir -p "$LOG_DIR" "$RUN_DIR"
cd "$ROOT"

if [[ -f "$PIDFILE" ]] && kill -0 "$(cat "$PIDFILE")" 2>/dev/null; then
  echo "operator already running with PID $(cat "$PIDFILE")"
  exit 0
fi

nohup "$PYTHON" "$ROOT/task_extract_send_rdp.py" >"$LOG" 2>&1 &
echo $! > "$PIDFILE"
echo "started operator pid=$! log=$LOG"
