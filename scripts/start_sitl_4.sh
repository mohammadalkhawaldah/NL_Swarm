#!/usr/bin/env bash
set -euo pipefail

ROOT=/home/mohd/NL_Swarm
LOG_DIR="$ROOT/logs"
mkdir -p "$LOG_DIR"
cd "$ROOT"

start_one() {
  local name="$1"
  shift
  local log="$LOG_DIR/${name}.log"
  if tmux has-session -t "$name" 2>/dev/null; then
    echo "$name already running"
    return 0
  fi
  : > "$log"
  tmux new-session -d -s "$name" "$*"
  echo "started $name"
}

start_one sitl_uav1 sim_vehicle.py -v ArduCopter --no-rebuild --out=udp:127.0.0.1:14550 --out=udp:127.0.0.1:14540 -L CMAC --add-param-file=battery_config.parm
start_one sitl_uav2 sim_vehicle.py -v ArduCopter --no-rebuild -I 1 --sysid 2 --out=udp:127.0.0.1:14550 --out=udp:127.0.0.1:14541 --custom-location=-35.363261,149.166230,584,353 --add-param-file=battery_config.parm
start_one sitl_uav3 sim_vehicle.py -v ArduCopter --no-rebuild -I 2 --sysid 3 --out=udp:127.0.0.1:14550 --out=udp:127.0.0.1:14542 --custom-location=-35.364261,149.165230,584,353 --add-param-file=battery_config.parm
start_one sitl_uav4 sim_vehicle.py -v ArduCopter --no-rebuild -I 3 --sysid 4 --out=udp:127.0.0.1:14550 --out=udp:127.0.0.1:14543 --custom-location=-35.365261,149.165230,584,353 --add-param-file=battery_config.parm
