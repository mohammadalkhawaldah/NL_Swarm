#!/usr/bin/env bash
set -euo pipefail

MAVSDK=/home/mohd/bin/mavsdk_server

start_one() {
  local name="$1"
  local grpc_port="$2"
  local udp_port="$3"
  if tmux has-session -t "$name" 2>/dev/null; then
    echo "$name already running"
    return 0
  fi
  tmux new-session -d -s "$name" "$MAVSDK -p $grpc_port udp://:$udp_port"
  echo "started $name"
}

start_one mavsdk_uav1 50040 14540
start_one mavsdk_uav2 50041 14541
start_one mavsdk_uav3 50042 14542
start_one mavsdk_uav4 50043 14543
