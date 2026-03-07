#!/usr/bin/env python3
"""
Experiment A1 Summary Data Collection Tool
Easy way to add experimental run data to the summary CSV
"""

import csv
from datetime import datetime
import os

SUMMARY_CSV = "experiment_A1_summary.csv"

def add_experiment_run():
    """Interactive tool to add a new experiment run"""
    print("=" * 60)
    print("EXPERIMENT A1 - ADD NEW RUN DATA")
    print("=" * 60)
    
    # Get basic info
    run_number = input("Run Number (002, 003, etc.): ").zfill(3)
    run_id = f"A1_{run_number}"
    timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    
    print(f"\nRun ID: {run_id}")
    print(f"Timestamp: {timestamp}")
    
    # Task information
    print("\n--- TASK INFORMATION ---")
    task_type = input("Task Type (delivery/survey/patrol/emergency): ").lower()
    task_location_name = input("Task Location Description: ")
    task_lat = float(input("Task Latitude: "))
    task_lon = float(input("Task Longitude: "))
    task_altitude = int(input("Task Altitude (meters): "))
    task_duration = input("Task Duration (e.g., 1min, 2min): ")
    
    # Agent data
    print("\n--- AGENT DATA ---")
    agents_data = {}
    
    for agent in ['uav1', 'uav2', 'uav3', 'uav4']:
        print(f"\n{agent.upper()}:")
        battery = input(f"  Battery start %: ")
        battery = int(battery) if battery.strip() else 0
        
        if battery == 0:
            # Agent eliminated
            agents_data[agent] = {
                'battery_start': 0,
                'distance': 'N/A',
                'phase1': 'FAIL',
                'bid_score': 'N/A',
                'specialization_bonus': 'N/A'
            }
        else:
            distance = float(input(f"  Distance to target (meters): "))
            phase1 = input(f"  Phase 1 result (PASS/FAIL): ").upper()
            
            if phase1 == 'PASS':
                bid_score = float(input(f"  Bid score: "))
                specialization = input(f"  Specialization bonus % (0 if none): ")
                specialization = float(specialization) / 100 if specialization.strip() else 0.0
            else:
                bid_score = 'N/A'
                specialization = 'N/A'
            
            agents_data[agent] = {
                'battery_start': battery,
                'distance': distance,
                'phase1': phase1,
                'bid_score': bid_score,
                'specialization_bonus': specialization
            }
    
    # Calculate summary stats
    total_agents = 4
    eligible_agents = sum(1 for agent in agents_data.values() if agent['phase1'] == 'PASS')
    bidding_agents = sum(1 for agent in agents_data.values() if agent['bid_score'] != 'N/A')
    eliminated_agents = total_agents - eligible_agents
    
    # Elimination reasons
    elimination_reasons = []
    for agent, data in agents_data.items():
        if data['phase1'] == 'FAIL':
            if data['battery_start'] == 0:
                elimination_reasons.append(f"{agent}: insufficient_battery")
            else:
                reason = input(f"Why was {agent} eliminated? ")
                elimination_reasons.append(f"{agent}: {reason}")
    
    elimination_reasons_str = "; ".join(elimination_reasons) if elimination_reasons else "none"
    
    # Winner information
    print("\n--- WINNER & MISSION RESULTS ---")
    winner_agent = input("Winner agent (uav1/uav2/uav3/uav4): ").lower()
    winner_score = float(input("Winner's bid score: "))
    
    # Calculate winning margin (difference to second place)
    bid_scores = [float(data['bid_score']) for data in agents_data.values() if data['bid_score'] != 'N/A']
    bid_scores.sort(reverse=True)
    winning_margin = bid_scores[0] - bid_scores[1] if len(bid_scores) > 1 else 0.0
    
    mission_success = input("Mission successful? (y/n): ").lower() == 'y'
    
    if mission_success:
        mission_duration = int(input("Actual mission duration (seconds): "))
        battery_consumed = int(input("Battery consumed (%): "))
        target_accuracy = float(input("Target accuracy (meters from target): "))
        energy_efficiency = agents_data[winner_agent]['distance'] / battery_consumed if battery_consumed > 0 else 0
    else:
        mission_duration = 0
        battery_consumed = 0
        target_accuracy = 'N/A'
        energy_efficiency = 0
    
    bidding_time = int(input("Bidding time (seconds, usually 3): ") or "3")
    total_mission_time = bidding_time + mission_duration
    
    notes = input("Additional notes: ")
    
    # Prepare row data
    row_data = [
        run_id,                           # run_id
        'A1',                            # experiment_id
        run_number,                      # run_number
        timestamp,                       # timestamp
        task_type,                       # task_type
        task_location_name,              # task_location_name
        task_lat,                        # task_lat
        task_lon,                        # task_lon
        task_altitude,                   # task_altitude
        task_duration,                   # task_duration
        total_agents,                    # total_agents
        eligible_agents,                 # eligible_agents
        bidding_agents,                  # bidding_agents
        eliminated_agents,               # eliminated_agents
        elimination_reasons_str,         # elimination_reasons
        agents_data['uav1']['battery_start'],    # uav1_battery_start
        agents_data['uav1']['distance'],         # uav1_distance
        agents_data['uav1']['phase1'],           # uav1_phase1
        agents_data['uav1']['bid_score'],        # uav1_bid_score
        agents_data['uav1']['specialization_bonus'], # uav1_specialization_bonus
        agents_data['uav2']['battery_start'],    # uav2_battery_start
        agents_data['uav2']['distance'],         # uav2_distance
        agents_data['uav2']['phase1'],           # uav2_phase1
        agents_data['uav2']['bid_score'],        # uav2_bid_score
        agents_data['uav2']['specialization_bonus'], # uav2_specialization_bonus
        agents_data['uav3']['battery_start'],    # uav3_battery_start
        agents_data['uav3']['distance'],         # uav3_distance
        agents_data['uav3']['phase1'],           # uav3_phase1
        agents_data['uav3']['bid_score'],        # uav3_bid_score
        agents_data['uav3']['specialization_bonus'], # uav3_specialization_bonus
        agents_data['uav4']['battery_start'],    # uav4_battery_start
        agents_data['uav4']['distance'],         # uav4_distance
        agents_data['uav4']['phase1'],           # uav4_phase1
        agents_data['uav4']['bid_score'],        # uav4_bid_score
        agents_data['uav4']['specialization_bonus'], # uav4_specialization_bonus
        winner_agent,                    # winner_agent
        winner_score,                    # winner_score
        round(winning_margin, 3),        # winning_margin
        mission_success,                 # mission_success
        mission_duration,                # mission_duration_actual
        battery_consumed,                # battery_consumed
        round(energy_efficiency, 2),     # energy_efficiency
        target_accuracy,                 # target_accuracy_meters
        bidding_time,                    # bidding_time_seconds
        total_mission_time,              # total_mission_time_seconds
        notes                            # notes
    ]
    
    # Append to CSV
    with open(SUMMARY_CSV, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(row_data)
    
    print(f"\n✅ Added run {run_id} to {SUMMARY_CSV}")
    print("=" * 60)

def view_summary_stats():
    """Show summary statistics from all runs"""
    if not os.path.exists(SUMMARY_CSV):
        print(f"No summary file found: {SUMMARY_CSV}")
        return
    
    with open(SUMMARY_CSV, 'r') as f:
        reader = csv.DictReader(f)
        runs = list(reader)
    
    if not runs:
        print("No runs recorded yet")
        return
    
    print("=" * 60)
    print("EXPERIMENT A1 - SUMMARY STATISTICS")
    print("=" * 60)
    
    total_runs = len(runs)
    successful_missions = sum(1 for run in runs if run['mission_success'] == 'TRUE')
    
    # Winner distribution
    winners = {}
    for run in runs:
        winner = run['winner_agent']
        winners[winner] = winners.get(winner, 0) + 1
    
    # Average metrics
    avg_eligible = sum(int(run['eligible_agents']) for run in runs) / total_runs
    avg_bidding = sum(int(run['bidding_agents']) for run in runs) / total_runs
    
    battery_consumptions = [int(run['battery_consumed']) for run in runs if run['battery_consumed'].isdigit()]
    avg_battery = sum(battery_consumptions) / len(battery_consumptions) if battery_consumptions else 0
    
    print(f"Total Runs: {total_runs}")
    print(f"Mission Success Rate: {successful_missions/total_runs*100:.1f}%")
    print(f"Average Eligible Agents: {avg_eligible:.1f}")
    print(f"Average Bidding Agents: {avg_bidding:.1f}")
    print(f"Average Battery Consumption: {avg_battery:.1f}%")
    print()
    print("Winner Distribution:")
    for winner, count in sorted(winners.items()):
        print(f"  {winner}: {count} wins ({count/total_runs*100:.1f}%)")
    
    print("=" * 60)

if __name__ == "__main__":
    while True:
        print("\nExperiment A1 Data Collection Tool")
        print("1. Add new experimental run")
        print("2. View summary statistics")
        print("3. Exit")
        
        choice = input("\nChoose option (1-3): ")
        
        if choice == '1':
            add_experiment_run()
        elif choice == '2':
            view_summary_stats()
        elif choice == '3':
            break
        else:
            print("Invalid choice")
