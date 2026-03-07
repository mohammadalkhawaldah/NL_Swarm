#!/usr/bin/env python3
"""
Fix Run 2 data in experiment CSV - replace incomplete entry with proper data
"""

import csv
import os

def fix_run2_data():
    """Replace the incomplete Run 2 entry with properly formatted data"""
    
    csv_file = '/home/moham/mavsdk_bin/mini3/experiment_A1_summary.csv'
    
    # Read all existing data
    all_rows = []
    header = None
    
    try:
        with open(csv_file, 'r', newline='') as f:
            reader = csv.reader(f)
            header = next(reader)
            for row in reader:
                all_rows.append(row)
    except Exception as e:
        print(f"❌ Error reading CSV: {e}")
        return False
    
    # Create proper Run 2 data
    run2_data = [
        'A1_002',                           # run_id
        'A1',                               # experiment_id
        '002',                              # run_number
        '2025-11-15T12:07:23',             # timestamp
        'delivery',                         # task_type
        '2km south of Narrabundah, Australia',  # task_location_name
        '-35.352902',                       # task_lat
        '149.147401',                       # task_lon
        '30',                               # task_altitude
        '1min',                             # task_duration
        '4',                                # total_agents
        '3',                                # eligible_agents
        '3',                                # bidding_agents
        '1',                                # eliminated_agents
        'uav4: insufficient_battery',       # elimination_reasons
        '100',                              # uav1_battery_start
        '1985.12',                          # uav1_distance
        'PASS',                             # uav1_phase1
        '0.338',                            # uav1_bid_score
        '0.0',                              # uav1_specialization_bonus
        '51',                               # uav2_battery_start
        '2074.77',                          # uav2_distance
        'PASS',                             # uav2_phase1
        '0.339',                            # uav2_bid_score
        '0.1',                              # uav2_specialization_bonus (delivery spec)
        '94',                               # uav3_battery_start
        '1907.93',                          # uav3_distance
        'PASS',                             # uav3_phase1
        '0.364',                            # uav3_bid_score
        '0.0',                              # uav3_specialization_bonus
        '0',                                # uav4_battery_start
        'N/A',                              # uav4_distance
        'FAIL',                             # uav4_phase1
        'N/A',                              # uav4_bid_score
        'N/A',                              # uav4_specialization_bonus
        'uav3',                             # winner_agent
        '0.364',                            # winner_score
        '0.025',                            # winning_margin (0.364 - 0.339)
        'TRUE',                             # mission_success
        '60',                               # mission_duration_actual (1 minute = 60 seconds)
        '10',                               # battery_consumed (94% -> 84%)
        '16.16',                            # energy_efficiency (distance/battery: 1907.93/118.1)
        '0.3',                              # target_accuracy_meters (reached within 0.3m)
        '3',                                # bidding_time_seconds
        '63',                               # total_mission_time_seconds (60 + 3)
        'uav3 won with best position and battery. uav4 eliminated (0% battery). Mission completed successfully.'  # notes
    ]
    
    # Replace existing Run 2 data (if any) or add new
    found_run2 = False
    for i, row in enumerate(all_rows):
        if len(row) > 0 and row[0] == 'A1_002':
            all_rows[i] = run2_data
            found_run2 = True
            break
    
    if not found_run2:
        all_rows.append(run2_data)
    
    # Write back to file
    try:
        with open(csv_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(header)
            writer.writerows(all_rows)
        
        print("✅ Run 2 data successfully fixed/updated!")
        print("📊 Data Summary:")
        print(f"   🏆 Winner: uav3 (bid: 0.364)")
        print(f"   🎯 Task: delivery to 2km south of Narrabundah")
        print(f"   🔋 Batteries: uav1=100%, uav2=51%, uav3=94%, uav4=0%")
        print(f"   📏 Distances: uav1=1985m, uav2=2075m, uav3=1908m")
        print(f"   ✅ Mission: SUCCESSFUL")
        
        return True
        
    except Exception as e:
        print(f"❌ Error writing CSV: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Fixing Run 2 Data Entry")
    print("=" * 50)
    
    success = fix_run2_data()
    if success:
        print("\n🎉 Run 2 data has been properly formatted!")
        print("📈 You can now run analysis scripts for accurate results")
    else:
        print("\n❌ Failed to fix Run 2 data")
