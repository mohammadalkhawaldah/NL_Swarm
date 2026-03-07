#!/usr/bin/env python3
"""
Simple task sender for testing - bypasses the complex extraction
"""

import socket, json, sys
from datetime import datetime

# Same multicast settings as agents
TASK_MCAST_GRP = "239.255.0.2"
TASK_MCAST_PORT = 30002

def send_task_multicast(task_data):
    """Send task to swarm via multicast"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 1)
        message = json.dumps(task_data).encode()
        sock.sendto(message, (TASK_MCAST_GRP, TASK_MCAST_PORT))
        sock.close()
        return True
    except Exception as e:
        print(f"❌ Multicast send failed: {e}")
        return False

def main():
    """Create and send a test delivery task"""
    
    # Create a test task similar to the one from your log
    task_dict = {
        "task_id": "delivery_test_001",
        "type": "delivery",
        "location": [-35.351464, 149.177974],  # The coordinates from your log
        "altitude": 20,
        "estimated_duration": "1min",
        "weather": "clear",
        "terrain": "urban",
        "priority": "normal",
        "description": "Test delivery to 5000m west of Queanbeyan High Australia",
        "timestamp": datetime.now().isoformat()
    }
    
    # Display the task
    print("🎯 TEST DELIVERY TASK")
    print("="*60)
    print(f"📋 Task ID: {task_dict['task_id']}")
    print(f"🎪 Type: {task_dict['type']}")
    print(f"📍 Location: {task_dict['location'][0]:.8f}, {task_dict['location'][1]:.8f}")
    print(f"🏷️ Location Name: 5000m west of Queanbeyan High Australia")
    print(f"🛫 Altitude: {task_dict['altitude']} meters")
    print(f"⏱️ Duration: {task_dict['estimated_duration']}")
    print(f"🌤️ Weather: {task_dict['weather']}")
    print(f"🏔️ Terrain: {task_dict['terrain']}")
    print(f"🚨 Priority: {task_dict['priority']}")
    print(f"📝 Description: {task_dict['description']}")
    print("="*60)
    
    # Confirm before sending
    sys.stdout.flush()  # Ensure all output is displayed
    send_confirm = input("\n✅ Send this task to drone agents? (y/n): ").strip().lower()
    
    if send_confirm not in ['y', 'yes']:
        print("❌ Task cancelled")
        return
    
    # Send task to agents
    print("\n📤 Sending task to drone agents...")
    print("📡 Attempting multicast delivery...")
    
    success = send_task_multicast(task_dict)
    
    if success:
        print("✅ Task sent via multicast to swarm!")
        print("\n🏆 Mission Status:")
        print("📊 Monitor agent terminals to see the bidding process")
        print("🥇 The winning drone will execute the mission")
        print("📤 Task delivery complete!")
    else:
        print("❌ Failed to send task to agents")

if __name__ == "__main__":
    main()
