#!/usr/bin/env bash
set -euo pipefail

scripts/start_sitl_4.sh
sleep 18
scripts/start_mavsdk_4.sh
sleep 6
scripts/start_agents_4.sh
