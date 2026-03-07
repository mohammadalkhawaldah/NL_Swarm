#!/usr/bin/env python3
"""
Data Collection Template for Experiment A1
Fill this out for each experimental run
"""

def create_csv_template(run_number, experiment_data):
    """
    Create CSV file for experiment run
    
    experiment_data should contain:
    - task_info: dict with task details
    - agents: dict with agent data
    - bidding_results: dict with bid scores and winner
    - mission_results: dict with execution results
    """
    
    filename = f"experiment_A1_run_{run_number:03d}.csv"
    
    # CSV Header
    header = [
        "experiment_id", "run_number", "timestamp", "agent_id", "event_type", 
        "task_id", "task_type", "location_lat", "location_lon", "altitude", 
        "duration", "battery_start", "battery_end", "distance_to_target", 
        "bid_score", "specialization_bonus", "winner", "phase1_result", 
        "phase1_reason", "mission_success", "mission_duration_actual", "notes"
    ]
    
    with open(filename, 'w') as f:
        f.write(','.join(header) + '\n')
        
        # Add rows based on experiment_data
        # This is a template - you'll fill this with actual data from each run
        
    print(f"Created template: {filename}")
    return filename

# Example of what data to collect for each run:
EXPERIMENT_A1_DATA_TEMPLATE = {
    'run_number': 2,  # Increment this for each run
    'timestamp': '2025-11-15T10:30:00',  # Start time
    'task_info': {
        'task_id': 'delivery_xxxx',
        'task_type': 'delivery',  # or 'survey', 'patrol', 'emergency'
        'location': {'lat': -35.351464, 'lon': 149.177974},
        'altitude': 30,
        'duration': '1min'
    },
    'agents': {
        'uav1': {'battery_start': 100, 'distance': 1748.22, 'phase1': 'PASS'},
        'uav2': {'battery_start': 50, 'distance': 1678.28, 'phase1': 'PASS'},  # Try different battery
        'uav3': {'battery_start': 80, 'distance': 1673.03, 'phase1': 'PASS'},
        'uav4': {'battery_start': 30, 'distance': 2000.0, 'phase1': 'PASS'}   # Try different position
    },
    'bidding_results': {
        'bids': {'uav1': 0.417, 'uav2': 0.485, 'uav3': 0.442, 'uav4': 0.380},
        'winner': 'uav2',
        'winner_score': 0.485
    },
    'mission_results': {
        'success': True,
        'duration_actual': 180,
        'battery_consumed': 12,
        'target_accuracy': 2.6
    }
}

print("=" * 60)
print("DATA COLLECTION GUIDE FOR EXPERIMENT A1")
print("=" * 60)
print()
print("For each experimental run, collect this data:")
print()
print("1. TASK INFORMATION:")
print("   - Task ID, type, location, altitude, duration")
print("   - Record from intent parser log")
print()
print("2. AGENT DATA (for each UAV):")
print("   - Starting battery percentage")
print("   - GPS position (for distance calculation)")
print("   - Phase 1 assessment result (PASS/FAIL)")
print("   - Reason for failure (if any)")
print()
print("3. BIDDING DATA:")
print("   - Bid score from each participating agent")
print("   - Specialization bonuses applied")
print("   - Winner announcement")
print()
print("4. MISSION EXECUTION (winner only):")
print("   - Mission success (TRUE/FALSE)")
print("   - Actual duration (seconds)")
print("   - Battery consumed (percentage)")
print("   - Final battery level")
print("   - Target reach accuracy (meters)")
print()
print("5. TIMING DATA:")
print("   - Task announcement time")
print("   - Bidding completion time")
print("   - Mission start time")
print("   - Mission completion time")
print()
print("VARIATIONS TO TEST (50 runs total):")
print("- Battery levels: 20%, 40%, 60%, 80%, 100%")
print("- Task types: delivery, survey, patrol, emergency")
print("- Agent positions: spread them out differently")
print("- Task locations: vary distance and direction")
print()
print("After each run:")
print("1. Save agent logs")
print("2. Fill out CSV file")
print("3. Run analysis script")
print("4. Note any anomalies or interesting behaviors")
