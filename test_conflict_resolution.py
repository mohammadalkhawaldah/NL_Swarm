#!/usr/bin/env python3
"""
UAV Conflict Resolution Test Script

This script simulates scenarios to test the winner announcement and 
conflict resolution protocol.

Usage:
    python test_conflict_resolution.py [test_case]

Test Cases:
    1 - Normal operation (clear winner)
    2 - Close race condition
    3 - Simultaneous tasks
    4 - All scenarios
"""

import json
import socket
import time
import sys

# Configuration
TASK_MCAST_GRP = "239.0.0.1"
TASK_MCAST_PORT = 5005

def send_task(task):
    """Send a task to the UAV swarm via multicast"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 1)
    
    task_json = json.dumps(task).encode()
    sock.sendto(task_json, (TASK_MCAST_GRP, TASK_MCAST_PORT))
    sock.close()
    
    print(f"✅ Sent task: {task['task_id']}")
    print(f"   Type: {task['type']}")
    print(f"   Location: {task['location']}")
    print()

def test_case_1():
    """Test Case 1: Normal Operation (No Conflict)
    
    Send a task to a location where D1 has clear advantage
    Expected: D1 wins cleanly, D2 acknowledges
    """
    print("=" * 60)
    print("TEST CASE 1: Normal Operation (Clear Winner)")
    print("=" * 60)
    print("\nObjective: Test normal operation with clear winner")
    print("Expected: D1 wins, others acknowledge, no conflicts\n")
    
    task = {
        "task_id": "test_normal_001",
        "type": "surveillance",
        "location": [-35.363261, 149.165230],  # Canberra (close to D1)
        "altitude": 50,
        "estimated_duration": "2min",
        "timestamp": time.time()
    }
    
    send_task(task)
    print("⏳ Wait 10 seconds and check logs for:")
    print("   ✅ D1 wins and executes")
    print("   ✅ D2+ receive win announcement")
    print("   ✅ No conflict warnings")
    print()

def test_case_2():
    """Test Case 2: Close Score Race Condition
    
    Send a task to a neutral location creating close scores
    Expected: Conflict resolution activates, one yields
    """
    print("=" * 60)
    print("TEST CASE 2: Race Condition (Close Scores)")
    print("=" * 60)
    print("\nObjective: Test conflict resolution with similar scores")
    print("Expected: Both announce win, lower score yields\n")
    
    task = {
        "task_id": "test_race_002",
        "type": "surveillance",
        "location": [-35.360, 149.160],  # Neutral location
        "altitude": 50,
        "estimated_duration": "2min",
        "timestamp": time.time()
    }
    
    send_task(task)
    print("⏳ Wait 10 seconds and check logs for:")
    print("   ✅ Multiple UAVs think they won")
    print("   ✅ Win announcements from multiple UAVs")
    print("   ✅ '⚠️ CONFLICT DETECTED' message")
    print("   ✅ '🛑 Yielding to' message")
    print("   ✅ Only one UAV executes mission")
    print()

def test_case_3():
    """Test Case 3: Simultaneous Tasks
    
    Send two tasks in quick succession
    Expected: Different winners, independent processing
    """
    print("=" * 60)
    print("TEST CASE 3: Simultaneous Tasks")
    print("=" * 60)
    print("\nObjective: Test independent task handling")
    print("Expected: Two different UAVs win two different tasks\n")
    
    task1 = {
        "task_id": "test_multi_003a",
        "type": "surveillance",
        "location": [-35.363261, 149.165230],  # Favors D1
        "altitude": 50,
        "estimated_duration": "1min",
        "timestamp": time.time()
    }
    
    task2 = {
        "task_id": "test_multi_003b",
        "type": "surveillance",
        "location": [-35.370, 149.180],  # Favors D2
        "altitude": 50,
        "estimated_duration": "1min",
        "timestamp": time.time() + 0.5
    }
    
    send_task(task1)
    time.sleep(1)
    send_task(task2)
    
    print("⏳ Wait 15 seconds and check logs for:")
    print("   ✅ Two different UAVs win")
    print("   ✅ Each task processed independently")
    print("   ✅ No cross-task interference")
    print()

def run_all_tests():
    """Run all test cases in sequence"""
    print("\n" + "=" * 60)
    print("RUNNING ALL TEST CASES")
    print("=" * 60 + "\n")
    
    test_case_1()
    input("Press Enter to continue to Test Case 2...")
    print()
    
    test_case_2()
    input("Press Enter to continue to Test Case 3...")
    print()
    
    test_case_3()
    print("\n✅ All test cases dispatched. Monitor UAV agent logs.")

def show_usage():
    """Show usage instructions"""
    print(__doc__)
    print("\nAvailable Commands:")
    print("  1 or normal     - Test normal operation")
    print("  2 or race       - Test race condition")
    print("  3 or multi      - Test simultaneous tasks")
    print("  all             - Run all tests")
    print("  help            - Show this message")

def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        show_usage()
        return
    
    arg = sys.argv[1].lower()
    
    if arg in ['1', 'normal']:
        test_case_1()
    elif arg in ['2', 'race']:
        test_case_2()
    elif arg in ['3', 'multi', 'simultaneous']:
        test_case_3()
    elif arg == 'all':
        run_all_tests()
    elif arg in ['help', '-h', '--help']:
        show_usage()
    else:
        print(f"❌ Unknown test case: {arg}")
        show_usage()

if __name__ == "__main__":
    main()
