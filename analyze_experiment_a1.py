#!/usr/bin/env python3
"""
Experiment A1 Data Analysis Script
Analyzes single task, multiple agents experiment data
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import numpy as np

def analyze_experiment_a1_run(csv_file):
    """Analyze a single run of Experiment A1"""
    print("=" * 60)
    print("EXPERIMENT A1 - DATA ANALYSIS")
    print("Single Task, Multiple Agents")
    print("=" * 60)
    
    # Read the data
    df = pd.read_csv(csv_file)
    
    # Basic experiment info
    experiment_id = df['experiment_id'].iloc[0]
    run_number = df['run_number'].iloc[0]
    task_id = df['task_id'].iloc[0]
    task_type = df['task_type'].iloc[0]
    
    print(f"Experiment ID: {experiment_id}")
    print(f"Run Number: {run_number}")
    print(f"Task ID: {task_id}")
    print(f"Task Type: {task_type}")
    print()
    
    # Agent participation analysis
    print("AGENT PARTICIPATION ANALYSIS")
    print("-" * 40)
    agents = df[df['agent_id'].str.startswith('uav')]['agent_id'].unique()
    
    for agent in sorted(agents):
        agent_data = df[df['agent_id'] == agent]
        battery_start = agent_data['battery_start'].iloc[0] if not agent_data.empty else 0
        phase1_result = agent_data[agent_data['event_type'] == 'phase1_assessment']['phase1_result'].iloc[0] if len(agent_data[agent_data['event_type'] == 'phase1_assessment']) > 0 else "N/A"
        bid_score = agent_data[agent_data['event_type'] == 'bid_submitted']['bid_score'].iloc[0] if len(agent_data[agent_data['event_type'] == 'bid_submitted']) > 0 else "N/A"
        
        print(f"{agent}: Battery={battery_start}%, Phase1={phase1_result}, Bid={bid_score}")
    
    print()
    
    # Bidding analysis
    print("BIDDING ANALYSIS")
    print("-" * 40)
    bid_data = df[df['event_type'] == 'bid_submitted'].copy()
    if not bid_data.empty:
        bid_data = bid_data.sort_values('bid_score', ascending=False)
        
        print("Bid Rankings:")
        for idx, row in bid_data.iterrows():
            rank = "🏆 WINNER" if row['agent_id'] == df[df['event_type'] == 'task_won']['agent_id'].iloc[0] else f"  Rank {len(bid_data) - list(bid_data.index).index(idx)}"
            specialization = f" (+{row['specialization_bonus']*100:.0f}% bonus)" if row['specialization_bonus'] > 0 else ""
            print(f"{rank} {row['agent_id']}: {row['bid_score']:.3f}{specialization}")
    
    print()
    
    # Mission execution analysis
    print("MISSION EXECUTION ANALYSIS")
    print("-" * 40)
    winner_data = df[df['event_type'] == 'task_won']
    if not winner_data.empty:
        winner = winner_data['agent_id'].iloc[0]
        mission_success = winner_data['mission_success'].iloc[0]
        battery_consumed = winner_data['battery_start'].iloc[0] - winner_data['battery_end'].iloc[0]
        mission_duration = winner_data['mission_duration_actual'].iloc[0]
        distance = winner_data['distance_to_target'].iloc[0]
        
        print(f"Winner: {winner}")
        print(f"Mission Success: {'✅ YES' if mission_success else '❌ NO'}")
        print(f"Distance Traveled: {distance:.2f} meters")
        print(f"Mission Duration: {mission_duration} seconds")
        print(f"Battery Consumed: {battery_consumed}%")
        print(f"Energy Efficiency: {distance/battery_consumed:.2f} meters per 1% battery")
    
    print()
    
    # Key metrics summary
    print("KEY METRICS SUMMARY")
    print("-" * 40)
    total_agents = len(agents)
    eligible_agents = len(df[df['phase1_result'] == 'PASS']['agent_id'].unique())
    bidding_agents = len(bid_data)
    mission_success_rate = 1 if df[df['mission_success'] == True].shape[0] > 0 else 0
    
    print(f"Total Agents: {total_agents}")
    print(f"Eligible Agents: {eligible_agents} ({eligible_agents/total_agents*100:.1f}%)")
    print(f"Bidding Agents: {bidding_agents}")
    print(f"Mission Success Rate: {mission_success_rate*100:.1f}%")
    
    # Response time (simplified - you'd need actual timestamps for precise measurement)
    print(f"System Response Time: ~3 seconds (bidding window)")
    
    return {
        'experiment_id': experiment_id,
        'run_number': run_number,
        'total_agents': total_agents,
        'eligible_agents': eligible_agents,
        'bidding_agents': bidding_agents,
        'mission_success_rate': mission_success_rate,
        'winner': winner_data['agent_id'].iloc[0] if not winner_data.empty else None,
        'winner_score': winner_data['bid_score'].iloc[0] if not winner_data.empty else None,
        'battery_consumed': battery_consumed if not winner_data.empty else None,
        'mission_duration': mission_duration if not winner_data.empty else None
    }

def create_comparison_chart(results_list):
    """Create comparison charts for multiple runs"""
    if len(results_list) < 2:
        print("Need at least 2 runs for comparison charts")
        return
    
    df_summary = pd.DataFrame(results_list)
    
    # Create visualization
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    
    # Agent participation rate
    axes[0,0].bar(['Eligible Agents'], [df_summary['eligible_agents'].mean()])
    axes[0,0].set_title('Average Eligible Agents')
    axes[0,0].set_ylabel('Count')
    
    # Mission success rate
    axes[0,1].bar(['Success Rate'], [df_summary['mission_success_rate'].mean() * 100])
    axes[0,1].set_title('Mission Success Rate (%)')
    axes[0,1].set_ylabel('Percentage')
    
    # Winner distribution
    winner_counts = df_summary['winner'].value_counts()
    axes[1,0].pie(winner_counts.values, labels=winner_counts.index, autopct='%1.1f%%')
    axes[1,0].set_title('Winner Distribution')
    
    # Battery consumption
    axes[1,1].hist(df_summary['battery_consumed'].dropna(), bins=5)
    axes[1,1].set_title('Battery Consumption Distribution')
    axes[1,1].set_xlabel('Battery Consumed (%)')
    axes[1,1].set_ylabel('Frequency')
    
    plt.tight_layout()
    plt.savefig('experiment_a1_analysis.png', dpi=300, bbox_inches='tight')
    plt.show()

if __name__ == "__main__":
    # Analyze the first run
    print("Analyzing Experiment A1 - Run 1...")
    results = analyze_experiment_a1_run("experiment_A1_run_001.csv")
    
    print("\n" + "="*60)
    print("ANALYSIS COMPLETE!")
    print("="*60)
    print("\nNext steps:")
    print("1. Run more iterations with different conditions")
    print("2. Vary battery levels (20%, 40%, 60%, 80%)")
    print("3. Change agent starting positions")
    print("4. Try different task types (survey, patrol, emergency)")
    print("5. Use create_comparison_chart() when you have multiple runs")
