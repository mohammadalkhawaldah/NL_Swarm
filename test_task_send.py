#!/usr/bin/env python3
"""
Quick test script to send a task to the agents
"""

import socket, json, time

# Same multicast settings as agents
TASK_MCAST_GRP = "239.255.0.2"
TASK_MCAST_PORT = 30002

def send_test_task():
    """Send a simple test task to agents"""
    task = {
        "task_id": "test_task_001",
        "type": "delivery",
        "location": [-35.351464, 149.177974],
        "altitude": 20,
        "estimated_duration": "1min",
        "weather": "clear",
        "terrain": "urban",
        "priority": "normal",
        "description": "Test delivery task",
        "timestamp": "2025-11-14T20:23:35"
    }
    
    try:
        # Create multicast socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 1)
        
        # Send task
        message = json.dumps(task).encode()
        sock.sendto(message, (TASK_MCAST_GRP, TASK_MCAST_PORT))
        sock.close()
        
        print(f"✅ Sent test task {task['task_id']} via multicast {TASK_MCAST_GRP}:{TASK_MCAST_PORT}")
        print(f"📋 Task: {task['type']} at {task['location']}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to send task: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing task communication to agents...")
    success = send_test_task()
    if success:
        print("✅ Task sent! Check agent terminals for reception.")
    else:
        print("❌ Task sending failed!")
