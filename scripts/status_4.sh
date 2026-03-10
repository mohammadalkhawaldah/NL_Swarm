#!/usr/bin/env bash
set -euo pipefail

for session in sitl_uav1 sitl_uav2 sitl_uav3 sitl_uav4 mavsdk_uav1 mavsdk_uav2 mavsdk_uav3 mavsdk_uav4 agent_uav1 agent_uav2 agent_uav3 agent_uav4 operator; do
  if tmux has-session -t "$session" 2>/dev/null; then
    echo "[$session] up"
  else
    echo "[$session] down"
  fi
done
