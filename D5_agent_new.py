#!/usr/bin/env python3
"""
D5_agent_new.py - UAV5 Agent with Two-Phase Task Selection
Config-driven: reads all assignments from drone_config.json
"""

import asyncio, json, socket, struct, time, math, random, threading, os, sys
from mavsdk import System

# --- Load config ---
CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'drone_config.json')
AGENT_ID = "uav5"

with open(CONFIG_PATH, 'r') as f:
    config = json.load(f)

my_cfg = config[AGENT_ID]
GRPC_HOST = "127.0.0.1"
GRPC_PORT = my_cfg["grpc_port"]
MY_BID_PORT = my_cfg["bid_port"]
PEER_BID_PORTS = [cfg["bid_port"] for aid, cfg in config.items() if aid != AGENT_ID]

PEER_MCAST_GRP = "239.255.0.1"
PEER_MCAST_PORT = 30001
PEER_HEARTBEAT_HZ = 2.0
TASK_MCAST_GRP = "239.255.0.2"
TASK_MCAST_PORT = 30002

peer_data = {}
task_scores = {}
score_lock = threading.Lock()

class DroneAgent:
    def __init__(self):
        self.drone_id = AGENT_ID
        self.mission_status = "idle"  # Track current mission status

    async def perform_self_assessment(self, drone, task):
        """Phase 1: Local suitability filtering"""
        print(f"\n[{self.drone_id}] 🔍 Phase 1: Self-Assessment for task {task.get('task_id', 'unknown')}")
        print(f"[{self.drone_id}] " + "=" * 50)

        # --- NEW: Check if busy ---
        # Only bid if not executing a mission, or if in RTL/idle states
        allowed_states = ["idle", "RTL", "LAND", "HOLD"]
        if self.mission_status not in allowed_states:
            print(f"[{self.drone_id}] 🛑 Not eligible: busy/executing mission ({self.mission_status})")
            log_event(
                agent_id=AGENT_ID,
                event_type="self_assessment",
                task_id=task.get("task_id"),
                phase="1",
                decision="not_eligible_busy"
            )
            return False

        capabilities_ok = await self.check_capabilities(task)
        resources_ok = await self.check_resources(drone, task)
        environment_ok = await self.check_environment(task)

        s_score = capabilities_ok and resources_ok and environment_ok
        print(f"\n[{self.drone_id}] 📊 Assessment Results:")
        print(f"   🔧 Capabilities: {'✅ PASS' if capabilities_ok else '❌ FAIL'}")
        print(f"   🔋 Resources: {'✅ PASS' if resources_ok else '❌ FAIL'}")
        print(f"   🌤️ Environment: {'✅ PASS' if environment_ok else '❌ FAIL'}")
        print(f"   🎯 Eligible: {'✅ YES' if s_score else '❌ NO'}")
        log_event(
            agent_id=AGENT_ID,
            event_type="self_assessment",
            task_id=task.get("task_id"),
            phase="1",
            decision="eligible" if s_score else "not_eligible"
        )
        return s_score

async def execute_mission(drone, task):
    agent = None
    # Find agent instance
    for obj in globals().values():
        if isinstance(obj, DroneAgent):
            agent = obj
            break
    if agent:
        agent.mission_status = "executing"
    print(f"\n[{AGENT_ID}] 🚀 Executing mission: {task['task_id']}")
    try:
        # --- NEW: Interrupt RTL if needed ---
        flight_mode = None
        try:
            async for mode in drone.telemetry.flight_mode():
                flight_mode = mode
                print(f"[{AGENT_ID}] Current flight mode: {flight_mode}")
                break
        except Exception as e:
            print(f"[{AGENT_ID}] ⚠️ Could not get flight mode: {e}")
        if flight_mode == "RTL":
            print(f"[{AGENT_ID}] 🛑 Interrupting RTL to start new mission!")
            try:
                await drone.action.set_mode("GUIDED")
                print(f"[{AGENT_ID}] ✅ Switched to GUIDED mode.")
            except Exception as e:
                print(f"[{AGENT_ID}] ⚠️ Could not switch to GUIDED: {e}")
        is_armed = False
        try:
            async for armed in drone.telemetry.armed():
                is_armed = armed
                print(f"[{AGENT_ID}] Armed state: {is_armed}")
                break
        except Exception as e:
            print(f"[{AGENT_ID}] ⚠️ Could not get armed state: {e}")
        altitude = task.get('altitude', 10)
        if not is_armed:
            await drone.action.set_takeoff_altitude(altitude)
            print(f"[{AGENT_ID}] Arming and taking off to {altitude}m...")
            await drone.action.arm()
            await drone.action.takeoff()
            print(f"[{AGENT_ID}] ⏳ Monitoring SITL telemetry until {altitude}m altitude reached...")
            takeoff_complete = False
            while not takeoff_complete:
                async for pos in drone.telemetry.position():
                    current_alt = pos.relative_altitude_m
                    if current_alt >= altitude - 1.0:
                        print(f"[{AGENT_ID}] ✅ Takeoff complete! SITL altitude: {current_alt:.1f}m")
                        takeoff_complete = True
                    else:
                        print(f"[{AGENT_ID}] 📈 Climbing... SITL reports: {current_alt:.1f}m / {altitude}m target")
                    break
                if not takeoff_complete:
                    await asyncio.sleep(0.5)
        else:
            print(f"[{AGENT_ID}] 🚁 Already airborne and armed, skipping takeoff.")
        # --- Execute mission task ---
        target_lat, target_lon = task.get('location', [-35.363261, 149.165230])
        print(f"[{AGENT_ID}] Flying to target: {target_lat}, {target_lon}")
        current_absolute_altitude = None
        async for pos in drone.telemetry.position():
            current_absolute_altitude = pos.absolute_altitude_m
            current_relative = pos.relative_altitude_m
            print(f"[{AGENT_ID}] ✈️ SITL telemetry - Relative: {current_relative:.1f}m, Absolute: {current_absolute_altitude:.1f}m")
            break
        if current_absolute_altitude is None:
            current_absolute_altitude = 550 + altitude
            print(f"[{AGENT_ID}] ⚠️ Using estimated absolute altitude: {current_absolute_altitude}m")
        await drone.action.goto_location(target_lat, target_lon, current_absolute_altitude, 0)
        print(f"[{AGENT_ID}] ⏳ Flying to target coordinates...")
        target_reached = False
        while not target_reached:
            async for pos in drone.telemetry.position():
                current_lat = pos.latitude_deg
                current_lon = pos.longitude_deg
                lat_diff = abs(current_lat - target_lat)
                lon_diff = abs(current_lon - target_lon)
                distance = math.sqrt(lat_diff**2 + lon_diff**2) * 111000
                if distance < 10.0:
                    print(f"[{AGENT_ID}] ✅ Reached target location (within {distance:.1f}m)")
                    target_reached = True
                    break
                if distance < 50.0:
                    print(f"[{AGENT_ID}] 📍 {distance:.1f}m from target...")
                break
            if not target_reached:
                await asyncio.sleep(2)
        duration_minutes = 1
        duration_str = task.get('estimated_duration', '1min')
        try:
            parsed = int(str(duration_str).replace('min', '').strip())
            if parsed == 2:
                duration_minutes = 2
        except Exception as e:
            print(f"[{AGENT_ID}] ⚠️ Duration parsing failed ({duration_str}): {e}, using 1min default")
            duration_minutes = 1
        mission_time = duration_minutes * 60
        print(f"[{AGENT_ID}] 🎯 At target! Executing mission for {duration_minutes} minutes...")
        await asyncio.sleep(mission_time)
        print(f"[{AGENT_ID}] Returning to launch...")
        await drone.action.return_to_launch()
        await asyncio.sleep(2)
        print(f"[{AGENT_ID}] ✅ Mission {task['task_id']} completed successfully!")
        # Log mission completion
        log_event(
            agent_id=AGENT_ID,
            event_type="mission_completed",
            task_id=task.get("task_id"),
            mission_status="completed",
            battery=task.get("battery"),
            lat=task.get("location")[0],
            lon=task.get("location")[1]
        )
        if agent:
            agent.mission_status = "RTL"  # Set to RTL after mission
    except Exception as e:
        print(f"[{AGENT_ID}] ❌ Mission execution error: {e}")
        # Log mission failure
        log_event(
            agent_id=AGENT_ID,
            event_type="mission_failed",
            task_id=task.get("task_id"),
            mission_status="failed",
            details=str(e)
        )
        if agent:
            agent.mission_status = "idle"  # Set to idle on failure
