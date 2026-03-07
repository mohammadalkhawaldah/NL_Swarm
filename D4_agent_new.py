#!/usr/bin/env python3
"""
D4_agent_new.py - UAV4 Agent with Two-Phase Task Selection
Fully config-driven: reads all assignments from drone_config.json
"""

import asyncio, json, socket, struct, time, math, random, threading, os, sys
from mavsdk import System

# --- Load config ---
CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'drone_config.json')
AGENT_ID = "uav4"

with open(CONFIG_PATH, 'r') as f:
    config = json.load(f)

my_cfg = config[AGENT_ID]
GRPC_HOST = "127.0.0.1"
GRPC_PORT = my_cfg["grpc_port"]
MY_BID_PORT = my_cfg["bid_port"]
PEER_BID_PORTS = [cfg["bid_port"] for aid, cfg in config.items() if aid != AGENT_ID]

PEER_MCAST_GRP = "239.255.0.1"
PEER_MCAST_PORT = 30001
PEER_HEARTBEAT_HZ = 0.2  # Reduced from 2.0 Hz to 0.2 Hz (once every 5 seconds)
TASK_MCAST_GRP = "239.255.0.2"
TASK_MCAST_PORT = 30002

peer_data = {}
task_scores = {}
score_lock = threading.Lock()

class DroneAgent:
    def __init__(self):
        self.drone_id = AGENT_ID
        self.mission_status = "idle"  # Track current mission status
        self.hardware_profile = {
            "thermal_camera": True,
            "standard_camera": True,
            "payload_release": True,
            "gps_precision": True,
            "communication": True
        }
        self.environmental_limits = {
            "max_wind_tolerance": 100,
            "min_temperature": -20,
            "max_temperature": 50,
            "rain_tolerance": True,
            "fog_tolerance": True
        }
    async def check_capabilities(self, task):
        task_type = task.get('type', '').lower()
        required_capabilities = []
        if task_type in ['sar', 'search', 'search_and_rescue']:
            required_capabilities.extend(['thermal_camera', 'gps_precision'])
        if 'rescue' in task.get('description', '').lower():
            required_capabilities.append('payload_release')
        for capability in required_capabilities:
            if not self.hardware_profile.get(capability, False):
                print(f"[{self.drone_id}] ❌ Missing capability: {capability}")
                return False
        print(f"[{self.drone_id}] ✅ All capabilities available")
        return True
    async def check_resources(self, drone, task):
        current_battery_percent = None
        if drone is not None:
            try:
                async for battery in drone.telemetry.battery():
                    current_battery_percent = battery.remaining_percent
                    voltage = battery.voltage_v
                    print(f"[{self.drone_id}] 🔋 Battery: {current_battery_percent:.1f}% ({voltage:.1f}V)")
                    break
            except Exception as e:
                print(f"[{self.drone_id}] ⚠️ Battery telemetry error: {e}")
        if current_battery_percent is None:
            current_battery_percent = 85.0
            print(f"[{self.drone_id}] 🔋 Simulated battery: {current_battery_percent}%")
        available_minutes = (current_battery_percent / 100.0) * 100
        duration_str = task.get('estimated_duration', '30min')
        if isinstance(duration_str, str):
            if 'min' in duration_str:
                required_minutes = float(duration_str.replace('min', '').strip())
            elif 'h' in duration_str:
                required_minutes = float(duration_str.replace('h', '').strip()) * 60
        else:
            required_minutes = float(duration_str)
        required_with_buffer = required_minutes * 1.25
        result = available_minutes > required_with_buffer
        print(f"[{self.drone_id}] 🔋 Need {required_with_buffer:.1f}min, have {available_minutes:.1f}min: {'✅ OK' if result else '❌ INSUFFICIENT'}")
        return result
    async def check_environment(self, task):
        weather = task.get('weather', 'clear').lower()
        terrain = task.get('terrain', 'flat').lower()
        unsuitable_weather = ['heavy_rain', 'storm', 'blizzard']
        if weather in unsuitable_weather:
            print(f"[{self.drone_id}] ❌ Unsuitable weather: {weather}")
            return False
        print(f"[{self.drone_id}] ✅ Environment suitable")
        return True
    def haversine(self, lat1, lon1, lat2, lon2):
        R = 6371000  # Earth radius in meters
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        dphi = math.radians(lat2 - lat1)
        dlambda = math.radians(lon2 - lon1)
        a = math.sin(dphi/2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c
    def calculate_bid_score(self, task, current_lat=None, current_lon=None):
        """Phase 2: Calculate competitive bid score using current UAV position
        Note: This function should only be called if GPS is healthy (current_lat/lon are valid)"""
        
        # Drone-specific home positions (unique for each UAV)
        home_positions = {
            "uav1": (-35.363261, 149.165230),    # CMAC
            "uav2": (-35.363261, 149.166230),    # CMAC_100M_EAST  
            "uav3": (-35.364261, 149.165230),    # SITL_3_LOCATION
            "uav4": (-35.365261, 149.165230),    # SITL_4_LOCATION
        }
        
        base_score = 1.0
        target_lat, target_lon = task.get('location', [-35.363261, 149.165230])
        
        if current_lat is not None and current_lon is not None:
            # Use current GPS position (recommended - real-time location)
            distance = self.haversine(current_lat, current_lon, target_lat, target_lon)
            print(f"[BID] Distance to target (from current GPS): {distance:.2f} meters")
        else:
            # This should rarely happen with GPS safety checks
            # But keeping for robustness with drone-specific home position
            home_lat, home_lon = home_positions.get(self.drone_id, (-35.363261, 149.165230))
            distance = self.haversine(home_lat, home_lon, target_lat, target_lon)
            print(f"[BID] ⚠️ Distance to target (from {self.drone_id} home): {distance:.2f} meters")
        
        distance_factor = max(0.1, 1.0 - (distance / 3000.0))
        task_type = task.get('type', '').lower()
        
        # UAV4 specialization: Better for delivery/cargo missions
        if task_type in ['delivery', 'cargo', 'supply']:
            capability_factor = 1.1
            print(f"[BID] {self.drone_id} specialization bonus: +10% for {task_type}")
        else:
            capability_factor = 1.0
        
        final_score = base_score * distance_factor * capability_factor
        return round(final_score, 3)
    async def perform_self_assessment(self, drone, task):
        """Phase 1: Local suitability filtering"""
        print(f"\n[{self.drone_id}] 🔍 Phase 1: Self-Assessment for task {task.get('task_id', 'unknown')}")
        print(f"[{self.drone_id}] " + "=" * 50)

        # --- NEW: Check if busy ---
        # Only bid if not executing a mission, or if in RTL/idle states
        allowed_states = ["idle", "RTL", "LAND", "HOLD"]
        if self.mission_status not in allowed_states:
            print(f"[{self.drone_id}] 🛑 Not eligible: busy/executing mission ({self.mission_status})")
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
        return s_score

def make_peer_tx_sock():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    s.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 1)
    return s

def make_peer_rx_sock():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        s.bind(("", PEER_MCAST_PORT))
    except OSError:
        s.bind((PEER_MCAST_GRP, PEER_MCAST_PORT))
    mreq = struct.pack("=4sl", socket.inet_aton(PEER_MCAST_GRP), socket.INADDR_ANY)
    s.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
    s.setblocking(False)
    return s

def make_task_rx_sock():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    s.bind(("", TASK_MCAST_PORT))
    mreq = struct.pack("=4sl", socket.inet_aton(TASK_MCAST_GRP), socket.INADDR_ANY)
    s.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
    s.setblocking(False)
    return s

def make_task_tx_sock():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    s.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 1)
    return s

def make_bid_tx_sock():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return s

def make_bid_rx_sock():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(("127.0.0.1", MY_BID_PORT))
    s.setblocking(False)
    print(f"[{AGENT_ID}] 🎯 Bidding RX: Listening on 127.0.0.1:{MY_BID_PORT}")
    return s

def send_p2p_message(message, peer_ports):
    """Send a message to all peer ports via P2P"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    msg_bytes = json.dumps(message).encode()
    for port in peer_ports:
        sock.sendto(msg_bytes, ("127.0.0.1", port))
    sock.close()

async def wait_connected(drone: System, timeout=30):
    async with asyncio.timeout(timeout):
        async for st in drone.core.connection_state():
            if st.is_connected:
                print(f"[{AGENT_ID}] Connected to mavsdk_server {GRPC_HOST}:{GRPC_PORT}")
                return
    raise TimeoutError("Connection timeout")

async def wait_basic_health(drone: System, timeout=60):
    async with asyncio.timeout(timeout):
        async for h in drone.telemetry.health():
            if (h.is_gyrometer_calibration_ok and
                h.is_accelerometer_calibration_ok and
                h.is_magnetometer_calibration_ok):
                print(f"[{AGENT_ID}] Sensors healthy")
                return
    raise TimeoutError("Health timeout")

async def publish_peer_state(drone: System, tx):
    period = 1.0 / PEER_HEARTBEAT_HZ
    last_status_print = 0.0
    global peer_data
    while True:
        # Get latest position
        try:
            pos = await drone.telemetry.position().__anext__()
        except Exception:
            await asyncio.sleep(period)
            continue
        now = time.time()
        battery_percent = None
        try:
            battery = await drone.telemetry.battery().__anext__()
            battery_percent = battery.remaining_percent
        except:
            battery_percent = 85.0
        msg = {
            "agent": AGENT_ID,
            "t": now,
            "lat": pos.latitude_deg,
            "lon": pos.longitude_deg,
            "alt": pos.relative_altitude_m,
            "battery": battery_percent
        }
        msg_bytes = json.dumps(msg).encode()
        tx.sendto(msg_bytes, (PEER_MCAST_GRP, PEER_MCAST_PORT))
        if now - last_status_print > 10.0:
            print(f"[{AGENT_ID}] 🔋 My battery: {battery_percent:.0f}% | Alt: {pos.relative_altitude_m:.1f}m")
            last_status_print = now
        await asyncio.sleep(period)

last_peer_log_time = {}  # Add this at the top-level (global)
last_seen = {}  # {peer_id: last_heartbeat_time}
HEARTBEAT_TIMEOUT = 10.0  # seconds
assigned_tasks = {}  # {peer_id: task_object}
lost_peers_set = set()  # Track already-logged lost peers

async def monitor_peers_and_rebid(drone, agent, bid_tx):
    global lost_peers_set
    while True:
        now = time.time()
        lost_peers = [peer for peer, t in last_seen.items() if now - t > HEARTBEAT_TIMEOUT]
        for lost_peer in lost_peers:
            if lost_peer not in lost_peers_set:
                print(f"[{AGENT_ID}] Peer lost: {lost_peer}")
                lost_peers_set.add(lost_peer)
            # If lost_peer had an assigned task, trigger re-bid:
            if lost_peer in assigned_tasks:
                task = assigned_tasks[lost_peer]
                task_id = task["task_id"] if isinstance(task, dict) and "task_id" in task else str(task)
                print(f"[{AGENT_ID}] Re-bidding task {task_id} due to lost peer {lost_peer}")
                # Actually trigger re-bid logic here
                await handle_task_selection(task, drone, agent, bid_tx)
                del assigned_tasks[lost_peer]
        # Remove from lost_peers_set if a heartbeat is received again
        for peer in list(lost_peers_set):
            if peer in last_seen and now - last_seen[peer] <= HEARTBEAT_TIMEOUT:
                lost_peers_set.remove(peer)
        await asyncio.sleep(2.0)

async def listen_peers(rx):
    loop = asyncio.get_running_loop()
    last_peer_print = 0.0
    global peer_data
    while True:
        try:
            data, _ = await loop.run_in_executor(None, rx.recvfrom, 2048)
            msg = json.loads(data.decode())
            peer_id = msg.get("agent")
            if peer_id and peer_id != AGENT_ID:
                peer_data[msg["agent"]] = {
                    "t": msg["t"],
                    "lat": msg["lat"],
                    "lon": msg["lon"],
                    "alt": msg["alt"],
                    "battery": msg.get("battery", 0)
                }
        except BlockingIOError:
            await asyncio.sleep(0.5)
        except Exception as e:
            print(f"[{AGENT_ID}] Peer RX error: {e}")
            await asyncio.sleep(1.0)

async def listen_tasks(rx, tx, drone, agent, bid_rx, bid_tx):
    loop = asyncio.get_running_loop()
    while True:
        try:
            data, _ = await loop.run_in_executor(None, rx.recvfrom, 4096)
            task = json.loads(data.decode())
            if "task_id" in task and "type" in task:
                await handle_task_selection(task, drone, agent, bid_tx)
        except BlockingIOError:
            await asyncio.sleep(0.05)
        except Exception as e:
            print(f"[{AGENT_ID}] Task RX error: {e}")
            await asyncio.sleep(0.2)

async def listen_bids(bid_rx):
    loop = asyncio.get_running_loop()
    global task_scores, score_lock
    while True:
        try:
            data, addr = await loop.run_in_executor(None, bid_rx.recvfrom, 1024)
            bid_msg = json.loads(data.decode())
            if "drone_id" in bid_msg and "score" in bid_msg:
                task_id = bid_msg.get("task_id")
                peer_id = bid_msg.get("drone_id")
                score = bid_msg.get("score")
                if task_id and peer_id:
                    with score_lock:
                        if task_id not in task_scores:
                            task_scores[task_id] = []
                        # Store entire message to preserve type field for win_announcement
                        if not any(s["drone_id"] == peer_id for s in task_scores[task_id]):
                            task_scores[task_id].append(bid_msg)
                    msg_type = bid_msg.get("type", "bid")
                    if msg_type == "win_announcement":
                        print(f"[{AGENT_ID}] 🏆 Received win announcement from {peer_id} for task {task_id}")
                    else:
                        print(f"[{AGENT_ID}] 📊 Received P2P bid from {peer_id}: {score} for task {task_id}")
        except BlockingIOError:
            await asyncio.sleep(0.05)
        except Exception as e:
            print(f"[{AGENT_ID}] Bid RX error: {e}")
            await asyncio.sleep(0.2)

async def handle_task_selection(task, drone, agent, bid_tx):
    """Handle the two-phase task selection process"""
    task_id = task["task_id"]
    eligible = await agent.perform_self_assessment(drone, task)
    if not eligible:
        print(f"[{AGENT_ID}] \U0001F6D1 Not eligible for task {task_id}")
        return
    # GPS Safety Check - Critical for UAV operations
    current_lat, current_lon = None, None
    gps_healthy = False
    
    try:
        # Check GPS health and get current position
        async for position in drone.telemetry.position():
            # Validate GPS coordinates (not zero and within reasonable bounds)
            if (position.latitude_deg != 0.0 and position.longitude_deg != 0.0 and
                abs(position.latitude_deg) <= 90.0 and abs(position.longitude_deg) <= 180.0):
                current_lat = position.latitude_deg
                current_lon = position.longitude_deg
                gps_healthy = True
                print(f"[{AGENT_ID}] ✅ GPS HEALTHY: Position {current_lat:.6f}, {current_lon:.6f}")
                break
            else:
                print(f"[{AGENT_ID}] ⚠️ Invalid GPS coordinates: {position.latitude_deg}, {position.longitude_deg}")
    except Exception as e:
        print(f"[{AGENT_ID}] ❌ GPS TELEMETRY FAILURE: {e}")
    
    # Safety Check: Abort mission if GPS is not available
    if not gps_healthy:
        print(f"[{AGENT_ID}] 🛑 MISSION ABORT: No valid GPS signal - Cannot participate in bidding")
        print(f"[{AGENT_ID}] 🔒 SAFETY REQUIREMENT: GPS lock required for autonomous operations")
        return
    # Phase 2: Competitive bidding
    print(f"\n[{AGENT_ID}] \U0001F4B0 Phase 2: Competitive Bidding for task {task_id}")
    my_score = agent.calculate_bid_score(task, current_lat, current_lon)
    score_msg = {
        "drone_id": AGENT_ID,
        "task_id": task_id,
        "score": my_score
    }
    for port in PEER_BID_PORTS:
        msg_bytes = json.dumps(score_msg).encode()
        bid_tx.sendto(msg_bytes, ("127.0.0.1", port))
    print(f"[{AGENT_ID}] \U0001F4E4 Sent P2P bid to peers: {my_score}")
    # 🚀 FAST BIDDING: Pre-check for scores that arrived early
    peer_scores = []
    with score_lock:
        if task_id in task_scores:
            for score_data in task_scores[task_id]:
                if score_data["drone_id"] != AGENT_ID:
                    peer_scores.append(score_data)
            del task_scores[task_id]
    print(f"[{AGENT_ID}] ⏳ Fast P2P bidding window (timeout: 3 seconds)...")
    await asyncio.sleep(0.2)
    timeout_time = time.time() + 3.0
    last_bid_print = 0.0
    while time.time() < timeout_time:
        with score_lock:
            if task_id in task_scores:
                for score_data in task_scores[task_id]:
                    if score_data["drone_id"] != AGENT_ID and score_data not in peer_scores:
                        peer_scores.append(score_data)
                del task_scores[task_id]
        now = time.time()
        if peer_scores and now - last_bid_print > 0.5:
            print(f"[{AGENT_ID}] 📊 My bid: {my_score} | Peer bid ({peer_scores[0]['drone_id']}): {peer_scores[0]['score']}")
            last_bid_print = now
            break
        await asyncio.sleep(0.1)
    await asyncio.sleep(0.1)
    with score_lock:
        if task_id in task_scores:
            for score_data in task_scores[task_id]:
                if score_data["drone_id"] != AGENT_ID and score_data not in peer_scores:
                    peer_scores.append(score_data)
            del task_scores[task_id]
    # After bidding window, collect all peer scores for this task
    with score_lock:
        if task_id in task_scores:
            for score_data in task_scores[task_id]:
                if score_data["drone_id"] != AGENT_ID and score_data not in peer_scores:
                    peer_scores.append(score_data)
            del task_scores[task_id]
    # Build all_scores with all unique drone_ids (including self)
    all_scores_dict = {AGENT_ID: my_score}
    for p in peer_scores:
        all_scores_dict[p["drone_id"]] = p["score"]
    all_scores = sorted(all_scores_dict.items(), key=lambda x: (-x[1], x[0]))
    winner_id, winner_score = all_scores[0]
    print(f"\n[{AGENT_ID}] \U0001F3C1 Bidding Results for task {task_id}:")
    for i, (drone_id, score) in enumerate(all_scores):
        status = "\U0001F3C6 WINNER" if i == 0 else "   "
        print(f"   {status} {drone_id}: {score}")
    if len(all_scores) == 1:
        print(f"[{AGENT_ID}] \u26A0\uFE0F No peer response received - winning by default")
    if winner_id == AGENT_ID:
        print(f"[{AGENT_ID}] \U0001F3C6 I WON! Executing task {task_id}")
        
        # Announce win to all peers
        win_announcement = {
            "type": "win_announcement",
            "task_id": task_id,
            "drone_id": AGENT_ID,
            "score": my_score,
            "timestamp": time.time()
        }
        send_p2p_message(win_announcement, PEER_BID_PORTS)
        
        # Wait briefly for conflict detection
        await asyncio.sleep(0.5)
        
        # Check if another drone also announced win with higher score
        conflict_detected = False
        with score_lock:
            if task_id in task_scores:
                for score_data in task_scores[task_id]:
                    if score_data.get("type") == "win_announcement" and score_data["drone_id"] != AGENT_ID:
                        if score_data["score"] > my_score:
                            print(f"[{AGENT_ID}] ⚠️ CONFLICT DETECTED: {score_data['drone_id']} also won with higher score ({score_data['score']} > {my_score})")
                            print(f"[{AGENT_ID}] 🛑 Yielding to {score_data['drone_id']}")
                            conflict_detected = True
                            assigned_tasks[score_data['drone_id']] = task
                            break
        
        if not conflict_detected:
            assigned_tasks[AGENT_ID] = task  # Track self-assignment (store full task)
            await execute_mission(drone, task)
    else:
        print(f"[{AGENT_ID}] \U0001F92C {winner_id} won. Standing by for next task.")
        assigned_tasks[winner_id] = task  # Track peer assignment (store full task)

async def execute_mission(drone, task):
    agent = None
    for obj in globals().values():
        if isinstance(obj, DroneAgent):
            agent = obj
            break
    if agent:
        agent.mission_status = "executing"
    print(f"\n[{AGENT_ID}] 🚀 Executing mission: {task['task_id']}")
    try:
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
        current_alt = 0.0
        try:
            async for armed in drone.telemetry.armed():
                is_armed = armed
                break
            async for pos in drone.telemetry.position():
                current_alt = pos.relative_altitude_m
                break
            print(f"[{AGENT_ID}] Armed state: {is_armed}, Altitude: {current_alt:.1f}m")
        except Exception as e:
            print(f"[{AGENT_ID}] ⚠️ Could not get armed/altitude state: {e}")
        altitude = task.get('altitude', 10)
        if not is_armed or current_alt < 2.0:
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
        # Get mission duration from task (force to 1 or 2 minutes only)
        duration_minutes = 1  # Default to 1 minute
        duration_str = task.get('estimated_duration', '1min')
        try:
            # Only allow 1 or 2 minutes
            parsed = int(str(duration_str).replace('min', '').strip())
            if parsed == 2:
                duration_minutes = 2
        except Exception as e:
            print(f"[{AGENT_ID}] ⚠️ Duration parsing failed ({duration_str}): {e}, using 1min default")
            duration_minutes = 1
        mission_time = duration_minutes * 60  # Convert to seconds
        print(f"[{AGENT_ID}] 🎯 At target! Executing mission for {duration_minutes} minutes...")
        await asyncio.sleep(mission_time)  # Execute mission for proper duration
        # Return to launch
        print(f"[{AGENT_ID}] Returning to launch...")
        await drone.action.return_to_launch()
        await asyncio.sleep(2)  # Reduced wait time after RTL
        print(f"[{AGENT_ID}] ✅ Mission {task['task_id']} completed successfully!")
        if agent:
            agent.mission_status = "RTL"  # Set to RTL after mission
    except Exception as e:
        print(f"[{AGENT_ID}] ❌ Mission execution error: {e}")
        if agent:
            agent.mission_status = "idle"  # Set to idle on failure

async def main():
    print(f"[{AGENT_ID}] 🚁 Starting UAV4 Agent with Two-Phase Task Selection")
    print(f"[{AGENT_ID}] Peer comm: {PEER_MCAST_GRP}:{PEER_MCAST_PORT}")
    print(f"[{AGENT_ID}] Task comm: {TASK_MCAST_GRP}:{TASK_MCAST_PORT}")
    print(f"[{AGENT_ID}] P2P Bidding: Listen={MY_BID_PORT}, Send={PEER_BID_PORTS}")
    print(f"[{AGENT_ID}] MAVSDK: {GRPC_HOST}:{GRPC_PORT}")
    agent = DroneAgent()
    drone = System(mavsdk_server_address=GRPC_HOST, port=GRPC_PORT)
    await drone.connect()
    await wait_connected(drone)
    await wait_basic_health(drone)
    peer_tx = make_peer_tx_sock()
    peer_rx = make_peer_rx_sock()
    task_tx = make_task_tx_sock()
    task_rx = make_task_rx_sock()
    bid_tx = make_bid_tx_sock()
    bid_rx = make_bid_rx_sock()
    print(f"[{AGENT_ID}] ✅ Ready for missions!")
    await asyncio.sleep(0.5)
    asyncio.create_task(monitor_peers_and_rebid(drone, agent, bid_tx))
    await asyncio.gather(
        publish_peer_state(drone, peer_tx),
        listen_peers(peer_rx),
        listen_tasks(task_rx, task_tx, drone, agent, bid_rx, bid_tx),
        listen_bids(bid_rx)
    )

if __name__ == "__main__":
    asyncio.run(main())
