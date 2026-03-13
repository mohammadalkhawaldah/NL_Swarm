#!/usr/bin/env python3
"""
Automatically add Run 2 data from log analysis
Extracts data from the provided log and adds to experiment CSV
"""

import csv
import os
from datetime import datetime

def add_run2_data():
    """Add Run 2 data extracted from the log to the experiment summary"""
    
    # Data extracted from the Run 2 log
    run_data = {
        'run_id': 'A1_002',
        'timestamp': '2025-11-15T12:07:23',  # From log timestamp
        'task_type': 'delivery',
        'task_location': '2km south of Narrabundah, Australia',
        'task_lat': -35.352902,
        'task_lon': 149.147401,
        'task_altitude': 30,
        'task_duration': 1,
        'winning_agent': 'uav3',
        'winning_bid': 0.364,
        'total_participants': 3,  # uav1, uav2, uav3 (uav4 ineligible)
        'eligible_agents': 3,
        'ineligible_agents': 1,  # uav4 (0% battery)
        'bid_uav1': 0.338,
        'bid_uav2': 0.339,
        'bid_uav3': 0.364,
        'bid_uav4': 'ineligible',
        'battery_uav1': 100,
        'battery_uav2': 51,
        'battery_uav3': 94,
        'battery_uav4': 0,
        'mission_success': 'yes',
        'mission_duration_actual': 1.0,  # From log: mission executed for 1 minute
        'distance_to_target_winner': 1907.93,  # From uav3 log
        'notes': 'uav4 ineligible due to 0% battery; uav3 won with best bid and closest distance'
    }
    
    # Path to summary CSV (in mini3 folder)
    summary_file = '/home/moham/mavsdk_bin/mini3/experiment_A1_summary.csv'
    
    # Check if summary file exists
    if not os.path.exists(summary_file):
        print(f"❌ Summary file not found: {summary_file}")
        print("Please make sure you're running this from the correct location")
        return False
    
    # Read existing data to avoid duplicates
    existing_runs = set()
    try:
        with open(summary_file, 'r', newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                existing_runs.add(row['run_id'])
    except Exception as e:
        print(f"❌ Error reading summary file: {e}")
        return False
    
    # Check if Run 2 already exists
    if run_data['run_id'] in existing_runs:
        print(f"⚠️  Run {run_data['run_id']} already exists in summary file")
        return False
    
    # Append new run data
    try:
        with open(summary_file, 'a', newline='') as f:
            fieldnames = [
                'run_id', 'timestamp', 'task_type', 'task_location', 'task_lat', 'task_lon',
                'task_altitude', 'task_duration', 'winning_agent', 'winning_bid',
                'total_participants', 'eligible_agents', 'ineligible_agents',
                'bid_uav1', 'bid_uav2', 'bid_uav3', 'bid_uav4',
                'battery_uav1', 'battery_uav2', 'battery_uav3', 'battery_uav4',
                'mission_success', 'mission_duration_actual', 'distance_to_target_winner', 'notes'
            ]
            
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writerow(run_data)
        
        print("✅ Run 2 data successfully added to experiment summary!")
        print(f"📊 Run ID: {run_data['run_id']}")
        print(f"🏆 Winner: {run_data['winning_agent']} (bid: {run_data['winning_bid']})")
        print(f"🎯 Task: {run_data['task_type']} at {run_data['task_location']}")
        print(f"🔋 Battery levels: uav1={run_data['battery_uav1']}%, uav2={run_data['battery_uav2']}%, uav3={run_data['battery_uav3']}%, uav4={run_data['battery_uav4']}%")
        
        return True
        
    except Exception as e:
        print(f"❌ Error writing to summary file: {e}")
        return False

def show_run2_summary():
    """Display a summary of the extracted Run 2 data"""
    print("=" * 70)
    print("📊 RUN 2 DATA EXTRACTION SUMMARY")
    print("=" * 70)
    print("📋 Task Details:")
    print("   • Type: delivery")
    print("   • Location: 2km south of Narrabundah, Australia")
    print("   • Coordinates: -35.352902, 149.147401")
    print("   • Altitude: 30m, Duration: 1 minute")
    print()
    print("🏆 Bidding Results:")
    print("   • uav3: 0.364 (WINNER) - 94% battery, 1907.93m from target")
    print("   • uav2: 0.339 - 51% battery, 2074.77m from target")  
    print("   • uav1: 0.338 - 100% battery, 1985.12m from target")
    print("   • uav4: INELIGIBLE - 0% battery")
    print()
    print("✅ Mission Status:")
    print("   • Winner: uav3")
    print("   • Execution: SUCCESSFUL")
    print("   • Duration: 1.0 minutes (as planned)")
    print("   • Battery consumption: 94% → 84% (10% used)")
    print("=" * 70)

if __name__ == "__main__":
    print("🤖 Automatic Run 2 Data Entry")
    print("=" * 70)
    
    # Show what data was extracted
    show_run2_summary()
    
    # Ask for confirmation
    response = input("\nAdd this data to experiment summary? (y/n): ").lower().strip()
    
    if response == 'y':
        success = add_run2_data()
        if success:
            print("\n🎉 Run 2 data has been added successfully!")
            print("📈 You can now run the analysis scripts to see updated statistics")
        else:
            print("\n❌ Failed to add Run 2 data")
    else:
        print("\n❌ Operation cancelled")
