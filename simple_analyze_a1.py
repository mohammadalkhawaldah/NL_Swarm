#!/usr/bin/env python3
"""
Simple Experiment A1 Data Analysis Script
Analyzes single task, multiple agents experiment data
"""

import csv
from collections import defaultdict

def analyze_experiment_a1_run(csv_file):
    """Analyze a single run of Experiment A1"""
    print("=" * 60)
    print("EXPERIMENT A1 - DATA ANALYSIS")
    print("Single Task, Multiple Agents")
    print("=" * 60)
    
    # Read the CSV data
    data = []
    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            data.append(row)
    
    if not data:
        print("No data found in CSV file")
        return
    
    # Basic experiment info
    experiment_id = data[0]['experiment_id']
    run_number = data[0]['run_number']
    task_id = data[0]['task_id']
    task_type = data[0]['task_type']
    
    print(f"Experiment ID: {experiment_id}")
    print(f"Run Number: {run_number}")
    print(f"Task ID: {task_id}")
    print(f"Task Type: {task_type}")
    print()
    
    # Agent participation analysis
    print("AGENT PARTICIPATION ANALYSIS")
    print("-" * 40)
    
    agents = {}
    for row in data:
        if row['agent_id'].startswith('uav'):
            if row['agent_id'] not in agents:
                agents[row['agent_id']] = {
                    'battery_start': row['battery_start'],
                    'phase1_result': 'N/A',
                    'bid_score': 'N/A',
                    'distance': row['distance_to_target']
                }
            
            if row['event_type'] == 'phase1_assessment':
                agents[row['agent_id']]['phase1_result'] = row['phase1_result']
            elif row['event_type'] == 'bid_submitted':
                agents[row['agent_id']]['bid_score'] = row['bid_score']
    
    for agent_id in sorted(agents.keys()):
        agent = agents[agent_id]
        battery = agent['battery_start']
        phase1 = agent['phase1_result']
        bid = agent['bid_score']
        distance = agent['distance'] if agent['distance'] != 'N/A' else 'N/A'
        
        print(f"{agent_id}: Battery={battery}%, Phase1={phase1}, Bid={bid}, Distance={distance}m")
    
    print()
    
    # Bidding analysis
    print("BIDDING ANALYSIS")
    print("-" * 40)
    
    bids = []
    winner = None
    
    for row in data:
        if row['event_type'] == 'bid_submitted':
            bids.append({
                'agent': row['agent_id'],
                'score': float(row['bid_score']),
                'specialization': float(row['specialization_bonus']) if row['specialization_bonus'] else 0
            })
        elif row['event_type'] == 'task_won':
            winner = row['agent_id']
    
    # Sort bids by score (highest first)
    bids.sort(key=lambda x: x['score'], reverse=True)
    
    print("Bid Rankings:")
    for i, bid in enumerate(bids):
        rank_symbol = "🏆 WINNER" if bid['agent'] == winner else f"  Rank {i+1}"
        specialization = f" (+{bid['specialization']*100:.0f}% bonus)" if bid['specialization'] > 0 else ""
        print(f"{rank_symbol} {bid['agent']}: {bid['score']:.3f}{specialization}")
    
    print()
    
    # Mission execution analysis
    print("MISSION EXECUTION ANALYSIS")
    print("-" * 40)
    
    for row in data:
        if row['event_type'] == 'task_won':
            winner_agent = row['agent_id']
            mission_success = row['mission_success'] == 'TRUE'
            battery_start = int(row['battery_start'])
            battery_end = int(row['battery_end'])
            battery_consumed = battery_start - battery_end
            mission_duration = int(row['mission_duration_actual'])
            distance = float(row['distance_to_target'])
            
            print(f"Winner: {winner_agent}")
            print(f"Mission Success: {'✅ YES' if mission_success else '❌ NO'}")
            print(f"Distance to Target: {distance:.2f} meters")
            print(f"Mission Duration: {mission_duration} seconds")
            print(f"Battery Consumed: {battery_consumed}%")
            if battery_consumed > 0:
                print(f"Energy Efficiency: {distance/battery_consumed:.2f} meters per 1% battery")
            break
    
    print()
    
    # Key metrics summary
    print("KEY METRICS SUMMARY")
    print("-" * 40)
    
    # Count metrics
    total_agents = len([row for row in data if row['agent_id'].startswith('uav') and row['event_type'] == 'task_received'])
    eligible_agents = len([row for row in data if row['event_type'] == 'phase1_assessment' and row['phase1_result'] == 'PASS'])
    bidding_agents = len([row for row in data if row['event_type'] == 'bid_submitted'])
    successful_missions = len([row for row in data if row['event_type'] == 'task_won' and row['mission_success'] == 'TRUE'])
    
    print(f"Total Agents: {total_agents}")
    print(f"Eligible Agents: {eligible_agents} ({eligible_agents/total_agents*100:.1f}%)")
    print(f"Bidding Agents: {bidding_agents}")
    print(f"Mission Success Rate: {successful_missions/1*100:.1f}%")  # Only 1 task in this experiment
    print(f"System Response Time: ~3 seconds (bidding window)")
    
    print("\n" + "="*60)
    print("ANALYSIS COMPLETE!")
    print("="*60)
    
    return {
        'total_agents': total_agents,
        'eligible_agents': eligible_agents,
        'bidding_agents': bidding_agents,
        'mission_success_rate': successful_missions,
        'winner': winner,
        'battery_consumed': battery_consumed if 'battery_consumed' in locals() else 0
    }

if __name__ == "__main__":
    # Analyze the first run
    print("Analyzing Experiment A1 - Run 1...")
    results = analyze_experiment_a1_run("experiment_A1_run_001.csv")
    
    print("\nNext steps for more experiments:")
    print("1. Run with different battery levels: 20%, 40%, 60%, 80%")
    print("2. Change agent starting positions")
    print("3. Try different task types: survey, patrol, emergency")
    print("4. Collect data from 50 runs total for statistical analysis")
    print("5. Create charts comparing winner patterns and efficiency")
