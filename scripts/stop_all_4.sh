#!/usr/bin/env bash
set -euo pipefail

for session in operator agent_uav1 agent_uav2 agent_uav3 agent_uav4 mavsdk_uav1 mavsdk_uav2 mavsdk_uav3 mavsdk_uav4 sitl_uav1 sitl_uav2 sitl_uav3 sitl_uav4; do
  tmux kill-session -t "$session" 2>/dev/null || true
done

pkill -f '/home/mohd/bin/mavsdk_server -p 5004[0-3]' || true
pkill -f 'D[1-4]_agent_new.py' || true
pkill -f 'task_extract_send_rdp.py' || true
