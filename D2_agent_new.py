#!/usr/bin/env python3
"""
D2_agent_new.py - UAV2 Agent with Two-Phase Task Selection  
Combines proven multicast communication with competitive task bidding
- Peer Communication: Multicast UDP 239.255.0.1:30001 (proven working)
- Task Communication: Multicast UDP 239.255.0.2:30002 (operator tasks)
- MAVSDK: gRPC port 50041 (UAV2, no cross-talk)
"""

import asyncio, json, socket, struct, time, math, random, threading, os
from mavsdk import System
from mavsdk.mission_raw import MissionItem as RawMissionItem
from swarm_search import (
    HOME_POSITIONS,
    approx_distance_m,
    build_centered_search_positions,
    build_team_positions,
    compute_search_partition_overview,
    compute_search_plan,
    ensure_search_task_defaults,
    local_m_to_latlon,
)
from map_visualizer_osm import open_search_partition_map

# --- Drone Configuration ---
CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'drone_config.json')
AGENT_ID = "uav2"
with open(CONFIG_PATH, 'r') as f:
    config = json.load(f)
my_cfg = config[AGENT_ID]
GRPC_HOST = "127.0.0.1"
GRPC_PORT = my_cfg["grpc_port"]
MY_BID_PORT = my_cfg["bid_port"]
PEER_BID_PORTS = [cfg["bid_port"] for aid, cfg in config.items() if aid != AGENT_ID]

# --- Peer Communication (PROVEN WORKING) ---
PEER_MCAST_GRP = "239.255.0.1"
PEER_MCAST_PORT = 30001
PEER_HEARTBEAT_HZ = 2.0  # Reduced from 5Hz to 2Hz for cleaner output

# --- Task Communication (HYBRID) ---
TASK_MCAST_GRP = "239.255.0.2"  
TASK_MCAST_PORT = 30002
ASSIGNMENT_MCAST_GRP = "239.255.0.3"
ASSIGNMENT_MCAST_PORT = 30003
COORD_HOST = "127.0.0.1"
COORD_PORT = 61000

# --- Point-to-Point Bidding (Fast like timing_synchronization.py) ---
UAV1_BID_PORT = 31001  # UAV1 listens for bids here
UAV2_BID_PORT = 31002  # UAV2 listens for bids here
MY_BID_PORT = UAV2_BID_PORT     # This agent (UAV2) listens here
PEER_BID_PORT = UAV1_BID_PORT   # Send bids to peer (UAV1) here

# --- Global state ---
peer_data = {}
# task_scores now maps task_id -> list of bid dicts
# Example: task_scores[task_id] = [bid1, bid2, ...]
task_scores = {}
score_lock = threading.Lock()

class DroneAgent:
    def __init__(self):
        self.drone_id = AGENT_ID
        self.mission_status = "idle"  # Track current mission status
        
        # Hardware profile (same as current working system)
        self.hardware_profile = {
            "thermal_camera": True,
            "standard_camera": True,
            "payload_release": True,
            "gps_precision": True,
            "communication": True
        }
        
        # Environmental limits (high tolerance for testing)
        self.environmental_limits = {
            "max_wind_tolerance": 100,   # km/hour
            "min_temperature": -20,      # °C
            "max_temperature": 50,       # °C
            "rain_tolerance": True,
            "fog_tolerance": True
        }

    async def check_capabilities(self, task):
        """Phase 1.1: Check hardware capabilities"""
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
        """Phase 1.2: Check battery resources (REAL telemetry)"""
        current_battery_percent = None
        
        if drone is not None:
            try:
                # Real battery telemetry (same as working system)
                async for battery in drone.telemetry.battery():
                    current_battery_percent = battery.remaining_percent
                    voltage = battery.voltage_v
                    print(f"[{self.drone_id}] 🔋 Battery: {current_battery_percent:.1f}% ({voltage:.1f}V)")
                    break
            except Exception as e:
                print(f"[{self.drone_id}] ⚠️ Battery telemetry error: {e}")
                
        if current_battery_percent is None:
            # Fallback for testing (clearly marked)
            current_battery_percent = 75.0  # UAV2 default (different from UAV1)
            print(f"[{self.drone_id}] 🔋 Simulated battery: {current_battery_percent}%")
        
        # Calculate flight time (30 min max at 100%)
        available_minutes = (current_battery_percent / 100.0) * 100
        
        # Parse task duration
        duration_str = task.get('estimated_duration', '30min')
        if isinstance(duration_str, str):
            if 'min' in duration_str:
                required_minutes = float(duration_str.replace('min', '').strip())
            elif 'h' in duration_str:
                required_minutes = float(duration_str.replace('h', '').strip()) * 60
        else:
            required_minutes = float(duration_str)
        
        # 25% safety buffer
        required_with_buffer = required_minutes * 1.25
        
        result = available_minutes > required_with_buffer
        print(f"[{self.drone_id}] 🔋 Need {required_with_buffer:.1f}min, have {available_minutes:.1f}min: {'✅ OK' if result else '❌ INSUFFICIENT'}")
        return result

    async def check_environment(self, task):
        """Phase 1.3: Check environmental conditions"""
        weather = task.get('weather', 'clear').lower()
        terrain = task.get('terrain', 'flat').lower()
        
        # Simple environment check (can be expanded)
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
        
        base_score = 1.0
        target_lat, target_lon = task.get('location', [-35.363261, 149.165230])
        
        if current_lat is not None and current_lon is not None:
            # Use current GPS position (recommended - real-time location)
            distance = self.haversine(current_lat, current_lon, target_lat, target_lon)
            print(f"[BID] Distance to target (from current GPS): {distance:.2f} meters")
        else:
            # This should rarely happen with GPS safety checks
            # But keeping for robustness with drone-specific home position
            home_lat, home_lon = HOME_POSITIONS.get(self.drone_id, (-35.363261, 149.165230))
            distance = self.haversine(home_lat, home_lon, target_lat, target_lon)
            print(f"[BID] ⚠️ Distance to target (from {self.drone_id} home): {distance:.2f} meters")
        
        distance_factor = max(0.1, 1.0 - (distance / 3000.0))
        task_type = task.get('type', '').lower()
        
        # UAV2 specialization: Better for delivery/cargo missions
        if task_type in ['delivery', 'cargo']:
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
        
        # ALL THREE must pass
        s_score = capabilities_ok and resources_ok and environment_ok
        
        print(f"\n[{self.drone_id}] 📊 Assessment Results:")
        print(f"   🔧 Capabilities: {'✅ PASS' if capabilities_ok else '❌ FAIL'}")
        print(f"   🔋 Resources: {'✅ PASS' if resources_ok else '❌ FAIL'}")
        print(f"   🌤️ Environment: {'✅ PASS' if environment_ok else '❌ FAIL'}")
        print(f"   🎯 Eligible: {'✅ YES' if s_score else '❌ NO'}")
        return s_score

# --- Communication Functions (PROVEN WORKING PATTERN) ---

def make_peer_tx_sock():
    """Create peer communication TX socket (same as working system)"""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    s.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 1)
    return s

def make_peer_rx_sock():
    """Create peer communication RX socket (same as working system)"""
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
    """Create task communication RX socket"""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)  # Allow port reuse
    s.bind(("", TASK_MCAST_PORT))
    mreq = struct.pack("=4sl", socket.inet_aton(TASK_MCAST_GRP), socket.INADDR_ANY)
    s.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
    s.setblocking(False)
    return s

def make_task_tx_sock():
    """Create task communication TX socket"""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    s.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 1)
    return s

def make_bid_tx_sock():
    """Create point-to-point bidding TX socket (fast like timing_synchronization.py)"""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return s

def make_bid_rx_sock():
    """Create point-to-point bidding RX socket (fast like timing_synchronization.py)"""
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
    async def _wait():
        async for st in drone.core.connection_state():
            if st.is_connected:
                print(f"[{AGENT_ID}] Connected to mavsdk_server {GRPC_HOST}:{GRPC_PORT}")
                return
    await asyncio.wait_for(_wait(), timeout=timeout)

async def wait_basic_health(drone: System, timeout=60):
    async def _wait():
        async for h in drone.telemetry.health():
            if (h.is_gyrometer_calibration_ok and
                h.is_accelerometer_calibration_ok and
                h.is_magnetometer_calibration_ok):
                print(f"[{AGENT_ID}] Sensors healthy")
                return
    await asyncio.wait_for(_wait(), timeout=timeout)

async def wait_navigation_ready(drone: System, timeout=120, settle_seconds=10.0):
    last_report = 0.0
    async def _wait():
        nonlocal last_report
        async for h in drone.telemetry.health():
            if time.time() - last_report > 2.0:
                print(
                    f"[{AGENT_ID}] Nav health: global={h.is_global_position_ok} "
                    f"home={h.is_home_position_ok} local={h.is_local_position_ok} armable={h.is_armable}"
                )
                last_report = time.time()
            if h.is_global_position_ok and h.is_home_position_ok and h.is_local_position_ok and h.is_armable:
                return
    await asyncio.wait_for(_wait(), timeout=timeout)
    print(f"[{AGENT_ID}] Navigation ready. Settling for {settle_seconds:.0f}s before flight command...")
    await asyncio.sleep(settle_seconds)

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
assignment_inbox = {}
assignment_events = {}


def get_assignment_slot(task_id):
    if task_id not in assignment_inbox:
        assignment_inbox[task_id] = {"current": None, "pending": None}
    if task_id not in assignment_events:
        assignment_events[task_id] = asyncio.Event()
    return assignment_inbox[task_id], assignment_events[task_id]


def make_assignment_rx_sock():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        s.bind(("", ASSIGNMENT_MCAST_PORT))
    except OSError:
        s.bind((ASSIGNMENT_MCAST_GRP, ASSIGNMENT_MCAST_PORT))
    mreq = struct.pack("=4sl", socket.inet_aton(ASSIGNMENT_MCAST_GRP), socket.INADDR_ANY)
    s.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
    s.setblocking(False)
    return s


def send_coord_message(payload):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.sendto(json.dumps(payload).encode("utf-8"), (COORD_HOST, COORD_PORT))
    finally:
        sock.close()

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
                last_seen[peer_id] = msg.get("t", time.time())
            if msg.get("agent") != AGENT_ID:
                peer_data[msg["agent"]] = {
                    "t": msg["t"],
                    "lat": msg["lat"],
                    "lon": msg["lon"],
                    "alt": msg["alt"],
                    "battery": msg.get("battery", 0)
                }
                # Clean old peers
                alive_peers = {k: v for k, v in peer_data.items() 
                              if time.time() - v["t"] < 3.0}
                peer_data.clear()
                peer_data.update(alive_peers)
                
                # Display peer info (only every 5 seconds)
                now = time.time()
                if now - last_peer_print > 5.0:
                    # Commented out battery display
                    """
                    peer_info = []
                    for peer_id, data in alive_peers.items():
                        battery = data.get("battery", 0)
                        peer_info.append(f"{peer_id}({battery:.0f}%)")
                    
                    if peer_info:
                        print(f"[{AGENT_ID}] Peers: {', '.join(peer_info)}")
                    else:
                        print(f"[{AGENT_ID}] No peers detected")
                    """
                    last_peer_print = now
                
        except BlockingIOError:
            await asyncio.sleep(0.5)  # Reduced frequency - check every 500ms instead of 50ms
        except Exception as e:
            print(f"[{AGENT_ID}] Peer RX error: {e}")
            await asyncio.sleep(1.0)  # Longer pause on errors

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

async def listen_assignments(rx):
    loop = asyncio.get_running_loop()
    while True:
        try:
            data, _ = await loop.run_in_executor(None, rx.recvfrom, 65535)
            payload = json.loads(data.decode())
            if payload.get("msg_type") != "region_assignment":
                continue
            if str(payload.get("drone_id")) != AGENT_ID:
                continue
            task_id = payload.get("task_id")
            if not task_id:
                continue
            slot, event = get_assignment_slot(task_id)
            if slot["current"] is None:
                slot["current"] = payload
                event.set()
            else:
                slot["pending"] = payload
            print(f"[{AGENT_ID}] Received assignment plan {payload.get('plan_id')} with {len(payload.get('cells', []))} cells")
        except BlockingIOError:
            await asyncio.sleep(0.05)
        except Exception as e:
            print(f"[{AGENT_ID}] Assignment RX error: {e}")
            await asyncio.sleep(0.2)

async def handle_task_selection(task, drone, agent, bid_tx):
    """Handle the two-phase task selection process"""
    task = ensure_search_task_defaults(task)
    task_id = task["task_id"]
    
    # Phase 1: Self-assessment
    eligible = await agent.perform_self_assessment(drone, task)
    
    if not eligible:
        print(f"[{AGENT_ID}] 🛑 Not eligible for task {task_id}")
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
    # 🚀 FAST BIDDING: Short delay and fast polling (like timing_synchronization.py)
    print(f"[{AGENT_ID}] ⏳ Fast P2P bidding window (timeout: 3 seconds)...")
    await asyncio.sleep(0.2)  # Very short initial delay for P2P setup
    
    timeout_time = time.time() + 3.0  # Back to 3s timeout for P2P (should be fast now)
    last_bid_print = 0.0
    
    while time.time() < timeout_time:
        with score_lock:
            if task_id in task_scores:
                for score_data in task_scores[task_id]:
                    if score_data["drone_id"] != AGENT_ID and score_data not in peer_scores:
                        peer_scores.append(score_data)
                del task_scores[task_id]
        await asyncio.sleep(0.1)
    with score_lock:
        if task_id in task_scores:
            for score_data in task_scores[task_id]:
                if score_data["drone_id"] != AGENT_ID and score_data not in peer_scores:
                    peer_scores.append(score_data)
            del task_scores[task_id]
    await asyncio.sleep(0.5)
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
    required_drones = max(1, int(task.get("required_drones", 1)))
    # Build all_scores with all unique drone_ids (including self)
    all_scores_dict = {AGENT_ID: my_score}
    for p in peer_scores:
        all_scores_dict[p["drone_id"]] = p["score"]
    all_scores = sorted(all_scores_dict.items(), key=lambda x: (-x[1], x[0]))
    selected_winners = [drone_id for drone_id, _ in all_scores[:required_drones]]
    print(f"\n[{AGENT_ID}] \U0001F3C1 Bidding Results for task {task_id}:")
    for i, (drone_id, score) in enumerate(all_scores):
        status = "\U0001F3C6 SELECTED" if drone_id in selected_winners else "   "
        print(f"   {status} {drone_id}: {score}")
    if len(all_scores) == 1:
        print(f"[{AGENT_ID}] \u26A0\uFE0F No peer response received - selected by default")
    if AGENT_ID in selected_winners:
        print(f"[{AGENT_ID}] \U0001F3C6 Selected for task {task_id}. Executing mission.")
        assigned_tasks[AGENT_ID] = task
        team_positions = build_team_positions(selected_winners, AGENT_ID, (current_lat, current_lon), peer_data)
        await execute_mission(drone, task, selected_winners, team_positions)
    else:
        print(f"[{AGENT_ID}] \U0001F92C Not selected. Standing by for next task.")
        for winner_id in selected_winners:
            assigned_tasks[winner_id] = task
    

async def wait_until_reached(drone, target_lat, target_lon, tolerance_m=10.0, timeout_s=240.0, progress_label="waypoint"):
    start_time = time.time()
    last_report = 0.0
    best_distance = None
    last_reissue = start_time

    while True:
        if time.time() - start_time > timeout_s:
            raise TimeoutError(f"Timed out reaching {progress_label}")

        async for pos in drone.telemetry.position():
            distance = approx_distance_m(pos.latitude_deg, pos.longitude_deg, target_lat, target_lon)
            if best_distance is None or distance < best_distance:
                best_distance = distance

            if distance < tolerance_m:
                print(f"[{AGENT_ID}] Reached {progress_label} within {distance:.1f}m")
                return

            now = time.time()
            if now - last_report >= 5.0:
                print(f"[{AGENT_ID}] {progress_label}: {distance:.1f}m remaining")
                last_report = now

            if best_distance is not None and distance > best_distance + 20.0 and now - last_reissue >= 15.0:
                print(f"[{AGENT_ID}] Reissuing command for {progress_label}")
                last_reissue = now
            break
        await asyncio.sleep(2)


async def goto_with_reissue(
    drone,
    target_lat,
    target_lon,
    absolute_altitude_m,
    tolerance_m=10.0,
    timeout_s=240.0,
    progress_label="waypoint",
    heading_deg=0.0,
):
    async def current_latlon():
        async for pos in drone.telemetry.position():
            return pos.latitude_deg, pos.longitude_deg

    async def fly_single_leg(leg_lat, leg_lon, leg_label):
        start_time = time.time()
        last_report = 0.0
        last_progress_time = start_time
        best_distance = None

        await drone.action.goto_location(leg_lat, leg_lon, absolute_altitude_m, heading_deg)

        while True:
            if time.time() - start_time > timeout_s:
                raise TimeoutError(f"Timed out reaching {leg_label}")

            async for pos in drone.telemetry.position():
                distance = approx_distance_m(pos.latitude_deg, pos.longitude_deg, leg_lat, leg_lon)
                now = time.time()

                if best_distance is None or distance < best_distance - 5.0:
                    best_distance = distance
                    last_progress_time = now

                if distance < tolerance_m:
                    print(f"[{AGENT_ID}] Reached {leg_label} within {distance:.1f}m")
                    return

                if now - last_report >= 5.0:
                    print(f"[{AGENT_ID}] {leg_label}: {distance:.1f}m remaining")
                    last_report = now

                if now - last_progress_time >= 12.0:
                    print(f"[{AGENT_ID}] Reissuing guided command for {leg_label}")
                    await drone.action.goto_location(leg_lat, leg_lon, absolute_altitude_m, heading_deg)
                    last_progress_time = now

                break
            await asyncio.sleep(2)

    start_lat, start_lon = await current_latlon()
    total_distance = approx_distance_m(start_lat, start_lon, target_lat, target_lon)
    max_segment_m = 120.0
    segment_count = max(1, int(math.ceil(total_distance / max_segment_m)))

    if segment_count == 1:
        await fly_single_leg(target_lat, target_lon, progress_label)
        return

    print(f"[{AGENT_ID}] {progress_label}: splitting into {segment_count} guided segments")
    for segment_idx in range(1, segment_count + 1):
        ratio = segment_idx / segment_count
        leg_lat = start_lat + (target_lat - start_lat) * ratio
        leg_lon = start_lon + (target_lon - start_lon) * ratio
        leg_label = f"{progress_label} segment {segment_idx}/{segment_count}"
        await fly_single_leg(leg_lat, leg_lon, leg_label)


def compute_stage_offset(selected_drones, drone_id):
    spacing = 30.0
    mapping = [
        (0.0, 0.0),
        (-spacing, -spacing),
        (-2 * spacing, -2 * spacing),
        (-spacing, spacing),
    ]
    try:
        idx = selected_drones.index(drone_id)
    except ValueError:
        idx = 0
    return mapping[min(idx, len(mapping) - 1)]


def apply_stage_offset(target_lat, target_lon, home_lat, home_lon, forward_offset_m, lateral_offset_m):
    meters_per_deg_lat = 111_320.0
    lat_rad = math.radians(home_lat)
    meters_per_deg_lon = 111_320.0 * math.cos(lat_rad)
    north_to_target = (target_lat - home_lat) * meters_per_deg_lat
    east_to_target = (target_lon - home_lon) * meters_per_deg_lon
    heading = math.atan2(east_to_target, north_to_target) if (north_to_target or east_to_target) else 0.0
    forward_north = math.cos(heading)
    forward_east = math.sin(heading)
    right_north = -math.sin(heading)
    right_east = math.cos(heading)
    offset_north = forward_offset_m * forward_north + lateral_offset_m * right_north
    offset_east = forward_offset_m * forward_east + lateral_offset_m * right_east
    return local_m_to_latlon(target_lat, target_lon, offset_east, offset_north)


async def wait_until_at_position(drone, target_lat, target_lon, target_alt_amsl, horiz_threshold_m=8.0, vert_threshold_m=3.0, label="waypoint"):
    async for position in drone.telemetry.position():
        horizontal = approx_distance_m(position.latitude_deg, position.longitude_deg, target_lat, target_lon)
        vertical = abs(position.absolute_altitude_m - target_alt_amsl)
        if horizontal <= horiz_threshold_m and vertical <= vert_threshold_m:
            print(f"[{AGENT_ID}] Reached {label}")
            return
        await asyncio.sleep(0.5)


async def goto_waypoint_and_wait(drone, latlon, altitude_amsl, label, horiz_threshold_m=8.0):
    lat, lon = latlon
    print(f"[{AGENT_ID}] Navigating to {label}: {lat:.6f}, {lon:.6f}")
    await drone.action.goto_location(lat, lon, altitude_amsl, float('nan'))
    await wait_until_at_position(
        drone,
        target_lat=lat,
        target_lon=lon,
        target_alt_amsl=altitude_amsl,
        horiz_threshold_m=horiz_threshold_m,
        vert_threshold_m=3.0,
        label=label,
    )


def convert_cells_to_local_points(cells, origin_xy, cell_size):
    ox, oy = origin_xy
    points = []
    for ix, iy in cells:
        x = ox + (ix + 0.5) * cell_size
        y = oy + (iy + 0.5) * cell_size
        points.append((ix, iy, x, y))
    return points


def build_snake_rows(points):
    rows = {}
    for ix, iy, x, y in points:
        rows.setdefault(iy, []).append((ix, iy, x, y))
    ordered_rows = []
    for idx, (_, row_cells) in enumerate(sorted(rows.items())):
        row_cells.sort(key=lambda item: item[0], reverse=(idx % 2 == 1))
        ordered_rows.append(row_cells)
    return ordered_rows


async def publish_search_state(drone, task, stop_event):
    target_lat, target_lon = task["location"]
    while not stop_event.is_set():
        try:
            async for pos in drone.telemetry.position():
                send_coord_message(
                    {
                        "msg_type": "state_update",
                        "task_id": task["task_id"],
                        "drone_id": AGENT_ID,
                        "selected_drones": task.get("selected_drones", []),
                        "target_lat": target_lat,
                        "target_lon": target_lon,
                        "search_radius_m": task["search_radius_m"],
                        "cell_size_m": task.get("lane_spacing_m", 30),
                        "activation_radius_m": min(140.0, max(80.0, task["search_radius_m"] * 0.35)),
                        "lat": pos.latitude_deg,
                        "lon": pos.longitude_deg,
                    }
                )
                break
        except Exception as e:
            print(f"[{AGENT_ID}] Search state publish error: {e}")
        await asyncio.sleep(1.0)


async def execute_assignment_rows(drone, task, assignment_state, search_alt_amsl):
    active_plan = assignment_state["current"]
    if not active_plan:
        return
    while active_plan:
        plan_id = active_plan["plan_id"]
        points = convert_cells_to_local_points(active_plan["cells"], tuple(active_plan["origin_xy"]), float(active_plan["cell_size"]))
        rows = build_snake_rows(points)
        for row_idx, row in enumerate(rows, start=1):
            start_ix, start_iy, start_x, start_y = row[0]
            end_ix, end_iy, end_x, end_y = row[-1]
            start_latlon = local_m_to_latlon(task["location"][0], task["location"][1], start_x, start_y)
            end_latlon = local_m_to_latlon(task["location"][0], task["location"][1], end_x, end_y)

            if row_idx == 1:
                corner_x = 0.0
                corner_y = start_y
                corner_latlon = local_m_to_latlon(task["location"][0], task["location"][1], corner_x, corner_y)
                await goto_waypoint_and_wait(drone, corner_latlon, search_alt_amsl, f"plan {plan_id} row {row_idx} entry corner", horiz_threshold_m=1.5)
                await goto_waypoint_and_wait(drone, start_latlon, search_alt_amsl, f"plan {plan_id} row {row_idx} start", horiz_threshold_m=1.5)
            else:
                prev_end_x = rows[row_idx - 2][-1][2]
                corner_latlon = local_m_to_latlon(task["location"][0], task["location"][1], prev_end_x, start_y)
                await goto_waypoint_and_wait(drone, corner_latlon, search_alt_amsl, f"plan {plan_id} row {row_idx} corner", horiz_threshold_m=1.5)
                if abs(start_x - prev_end_x) > 1.0:
                    await goto_waypoint_and_wait(drone, start_latlon, search_alt_amsl, f"plan {plan_id} row {row_idx} start", horiz_threshold_m=1.5)

            if abs(end_x - start_x) > 1.0 or abs(end_y - start_y) > 1.0:
                await goto_waypoint_and_wait(drone, end_latlon, search_alt_amsl, f"plan {plan_id} row {row_idx} end", horiz_threshold_m=1.5)

            send_coord_message(
                {
                    "msg_type": "coverage_update",
                    "task_id": task["task_id"],
                    "drone_id": AGENT_ID,
                    "plan_id": plan_id,
                    "cells": [[ix, iy] for ix, iy, _, _ in row],
                }
            )
            if assignment_state["pending"]:
                print(f"[{AGENT_ID}] Switching to pending assignment after row {row_idx}")
                assignment_state["current"] = assignment_state["pending"]
                assignment_state["pending"] = None
                active_plan = assignment_state["current"]
                break
        else:
            assignment_state["current"] = None
            active_plan = assignment_state["pending"]
            assignment_state["pending"] = None
            if active_plan:
                assignment_state["current"] = active_plan
        await asyncio.sleep(0.5)


async def execute_search_mission(drone, task, current_absolute_altitude, selected_drones, team_positions):
    target_lat, target_lon = task["location"]
    centered_positions = build_centered_search_positions(selected_drones, target_lat, target_lon)
    rendezvous_lat, rendezvous_lon = centered_positions.get(AGENT_ID, (target_lat, target_lon))
    print(f"[{AGENT_ID}] Navigating to search rendezvous at {rendezvous_lat:.6f}, {rendezvous_lon:.6f}")
    await goto_waypoint_and_wait(drone, (rendezvous_lat, rendezvous_lon), current_absolute_altitude, "search rendezvous")
    await asyncio.sleep(2.0)

    task["selected_drones"] = list(selected_drones)
    assignment_state, assignment_event = get_assignment_slot(task["task_id"])
    assignment_state["current"] = None
    assignment_state["pending"] = None
    assignment_event.clear()

    send_coord_message(
        {
            "msg_type": "search_registration",
            "task_id": task["task_id"],
            "drone_id": AGENT_ID,
            "selected_drones": list(selected_drones),
            "target_lat": target_lat,
            "target_lon": target_lon,
            "search_radius_m": task["search_radius_m"],
            "cell_size_m": task.get("lane_spacing_m", 30),
            "activation_radius_m": min(140.0, max(80.0, task["search_radius_m"] * 0.35)),
            "x_local": 0.0,
            "y_local": 0.0,
        }
    )

    stop_event = asyncio.Event()
    publisher = asyncio.create_task(publish_search_state(drone, task, stop_event))
    try:
        await asyncio.wait_for(assignment_event.wait(), timeout=60.0)
        if AGENT_ID == selected_drones[0]:
            try:
                overview = compute_search_partition_overview(task, selected_drones, centered_positions)
                open_search_partition_map(task, overview)
            except Exception as e:
                print(f"[{AGENT_ID}] Could not open search partition map: {e}")
        print(f"[{AGENT_ID}] Received coordinator assignment, starting row coverage")
        await execute_assignment_rows(drone, task, assignment_state, current_absolute_altitude)
        print(f"[{AGENT_ID}] Coordinator-driven coverage complete")
    finally:
        stop_event.set()
        publisher.cancel()
        await asyncio.gather(publisher, return_exceptions=True)


async def clear_previous_vehicle_paths(drone):
    """Clear previously uploaded mission items before starting a new task."""
    try:
        await drone.mission_raw.clear_mission()
        print(f"[{AGENT_ID}] Cleared previous raw mission items")
    except Exception as e:
        print(f"[{AGENT_ID}] Could not clear raw mission items: {e}")

    mission_iface = getattr(drone, "mission", None)
    if mission_iface is not None:
        try:
            await mission_iface.clear_mission()
            print(f"[{AGENT_ID}] Cleared previous mission plan")
        except Exception:
            pass


async def execute_mission(drone, task, selected_drones=None, team_positions=None):
    agent = None
    for obj in globals().values():
        if isinstance(obj, DroneAgent):
            agent = obj
            break
    if agent:
        agent.mission_status = "executing"
    print(f"\n[{AGENT_ID}] Executing mission: {task['task_id']}")

    try:
        await clear_previous_vehicle_paths(drone)

        flight_mode = None
        try:
            async for mode in drone.telemetry.flight_mode():
                flight_mode = mode
                print(f"[{AGENT_ID}] Current flight mode: {flight_mode}")
                break
        except Exception as e:
            print(f"[{AGENT_ID}] Could not get flight mode: {e}")

        mode_name = getattr(flight_mode, "name", str(flight_mode))
        if mode_name == "RETURN_TO_LAUNCH":
            print(f"[{AGENT_ID}] Interrupting RTL to start new mission")
            try:
                await drone.action.hold()
                print(f"[{AGENT_ID}] Switched to HOLD mode")
            except Exception as e:
                print(f"[{AGENT_ID}] Could not switch to HOLD: {e}")

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
            print(f"[{AGENT_ID}] Could not get armed/altitude state: {e}")

        altitude = task.get('altitude', 10)
        if current_alt < 2.0:
            await wait_navigation_ready(drone)
            await drone.action.set_takeoff_altitude(altitude)
            if not is_armed:
                print(f"[{AGENT_ID}] Arming and taking off to {altitude}m...")
                await drone.action.arm()
            else:
                print(f"[{AGENT_ID}] Armed on ground. Re-arming cleanly before takeoff...")
                try:
                    await drone.action.disarm()
                    await asyncio.sleep(1.0)
                except Exception as e:
                    print(f"[{AGENT_ID}] Disarm before retry failed: {e}")
                await drone.action.arm()
            await asyncio.sleep(2.0)
            try:
                await drone.action.takeoff()
            except Exception as e:
                if is_armed:
                    print(f"[{AGENT_ID}] Initial takeoff failed while armed on ground: {e}")
                    print(f"[{AGENT_ID}] Retrying takeoff after arm reset...")
                    await drone.action.disarm()
                    await asyncio.sleep(1.0)
                    await drone.action.arm()
                    await drone.action.takeoff()
                else:
                    raise
            print(f"[{AGENT_ID}] Monitoring telemetry until {altitude}m altitude reached...")
            takeoff_complete = False
            while not takeoff_complete:
                async for pos in drone.telemetry.position():
                    current_alt = pos.relative_altitude_m
                    if current_alt >= altitude - 1.0:
                        print(f"[{AGENT_ID}] Takeoff complete. Altitude: {current_alt:.1f}m")
                        takeoff_complete = True
                    else:
                        print(f"[{AGENT_ID}] Climbing... {current_alt:.1f}m / {altitude}m target")
                    break
                if not takeoff_complete:
                    await asyncio.sleep(0.5)
        else:
            print(f"[{AGENT_ID}] Already airborne and armed, skipping takeoff.")

        target_lat, target_lon = task.get('location', [-35.363261, 149.165230])
        print(f"[{AGENT_ID}] Flying to target: {target_lat}, {target_lon}")
        current_absolute_altitude = None
        async for pos in drone.telemetry.position():
            current_absolute_altitude = pos.absolute_altitude_m
            current_relative = pos.relative_altitude_m
            print(f"[{AGENT_ID}] SITL telemetry - Relative: {current_relative:.1f}m, Absolute: {current_absolute_altitude:.1f}m")
            break
        if current_absolute_altitude is None:
            current_absolute_altitude = 550 + altitude
            print(f"[{AGENT_ID}] Using estimated absolute altitude: {current_absolute_altitude}m")

        if str(task.get("type", "")).lower() == "search" and selected_drones and team_positions:
            await execute_search_mission(drone, task, current_absolute_altitude, selected_drones, team_positions)
        else:
            print(f"[{AGENT_ID}] Flying to target coordinates...")
            await goto_with_reissue(
                drone,
                target_lat,
                target_lon,
                current_absolute_altitude,
                tolerance_m=15.0,
                timeout_s=240.0,
                progress_label="target",
            )

        if str(task.get("type", "")).lower() == "search":
            print(f"[{AGENT_ID}] Search coverage complete. Returning without extra hover.")
        else:
            duration_minutes = 3
            duration_str = task.get('estimated_duration', '3min')
            try:
                parsed = int(str(duration_str).replace('min', '').strip())
                if parsed == 2:
                    duration_minutes = 2
            except Exception as e:
                print(f"[{AGENT_ID}] Duration parsing failed ({duration_str}): {e}, using 3min default")
                duration_minutes = 3
            mission_time = duration_minutes * 60
            print(f"[{AGENT_ID}] At target. Executing mission for {duration_minutes} minutes...")
            await asyncio.sleep(mission_time)

        print(f"[{AGENT_ID}] Returning to launch...")
        await drone.action.return_to_launch()
        await asyncio.sleep(2)
        print(f"[{AGENT_ID}] Mission {task['task_id']} completed successfully!")
        if agent:
            agent.mission_status = "RTL"
    except Exception as e:
        print(f"[{AGENT_ID}] Mission execution error: {e}")
        if agent:
            agent.mission_status = "idle"

async def main():
    print("[DEBUG] Entered main() for UAV2")
    print(f"[{AGENT_ID}] 🚁 Starting UAV2 Agent with Two-Phase Task Selection")
    print(f"[{AGENT_ID}] Peer comm: {PEER_MCAST_GRP}:{PEER_MCAST_PORT}")
    print(f"[{AGENT_ID}] Task comm: {TASK_MCAST_GRP}:{TASK_MCAST_PORT}")
    print(f"[{AGENT_ID}] P2P Bidding: Listen={MY_BID_PORT}, Send={PEER_BID_PORT}")
    print(f"[{AGENT_ID}] MAVSDK: {GRPC_HOST}:{GRPC_PORT}")
    # Initialize agent
    agent = DroneAgent()
    # Connect to MAVSDK
    drone = System(mavsdk_server_address=GRPC_HOST, port=GRPC_PORT)
    await drone.connect()
    await wait_connected(drone)
    await wait_basic_health(drone)
    # Create sockets
    peer_tx = make_peer_tx_sock()
    peer_rx = make_peer_rx_sock()
    task_tx = make_task_tx_sock()
    task_rx = make_task_rx_sock()
    bid_tx = make_bid_tx_sock()
    bid_rx = make_bid_rx_sock()
    assignment_rx = make_assignment_rx_sock()
    print(f"[{AGENT_ID}] ✅ Ready for missions!")
    await asyncio.sleep(0.5)
    asyncio.create_task(monitor_peers_and_rebid(drone, agent, bid_tx))
    await asyncio.gather(
        publish_peer_state(drone, peer_tx),
        listen_peers(peer_rx),
        listen_tasks(task_rx, task_tx, drone, agent, bid_rx, bid_tx),
        listen_bids(bid_rx),
        listen_assignments(assignment_rx),
    )

if __name__ == "__main__":
    asyncio.run(main())
