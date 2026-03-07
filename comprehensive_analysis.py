#!/usr/bin/env python3
"""
Experiment A1 Comprehensive Analysis Script
Analyzes trends and patterns across multiple experimental runs
"""

import csv
import os
from collections import defaultdict, Counter

def analyze_summary_data(csv_file="experiment_A1_summary.csv"):
    """Comprehensive analysis of all experimental runs"""
    
    if not os.path.exists(csv_file):
        print(f"Summary file not found: {csv_file}")
        return
    
    # Read all data
    runs = []
    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)
        runs = list(reader)
    
    if not runs:
        print("No experimental data found")
        return
    
    print("=" * 80)
    print("EXPERIMENT A1 - COMPREHENSIVE ANALYSIS")
    print(f"Analysis of {len(runs)} experimental runs")
    print("=" * 80)
    
    # Basic Statistics
    print("\n📊 BASIC STATISTICS")
    print("-" * 40)
    
    total_runs = len(runs)
    successful_missions = sum(1 for run in runs if run['mission_success'] == 'TRUE')
    success_rate = successful_missions / total_runs * 100
    
    print(f"Total Experimental Runs: {total_runs}")
    print(f"Successful Missions: {successful_missions}")
    print(f"Mission Success Rate: {success_rate:.1f}%")
    
    # Agent Participation Analysis
    print("\n👥 AGENT PARTICIPATION ANALYSIS")
    print("-" * 40)
    
    total_eligible = sum(int(run['eligible_agents']) for run in runs)
    total_bidding = sum(int(run['bidding_agents']) for run in runs)
    total_eliminated = sum(int(run['eliminated_agents']) for run in runs)
    
    print(f"Average Eligible Agents per Run: {total_eligible/total_runs:.1f}")
    print(f"Average Bidding Agents per Run: {total_bidding/total_runs:.1f}")
    print(f"Average Eliminated Agents per Run: {total_eliminated/total_runs:.1f}")
    print(f"Overall Participation Rate: {total_eligible/(total_runs*4)*100:.1f}%")
    
    # Winner Distribution Analysis
    print("\n🏆 WINNER DISTRIBUTION ANALYSIS")
    print("-" * 40)
    
    winners = Counter(run['winner_agent'] for run in runs)
    for agent in ['uav1', 'uav2', 'uav3', 'uav4']:
        wins = winners.get(agent, 0)
        win_rate = wins / total_runs * 100
        print(f"{agent.upper()}: {wins} wins ({win_rate:.1f}%)")
    
    # Task Type Analysis
    print("\n📋 TASK TYPE ANALYSIS")
    print("-" * 40)
    
    task_types = Counter(run['task_type'] for run in runs)
    for task_type, count in task_types.most_common():
        percentage = count / total_runs * 100
        task_success = sum(1 for run in runs if run['task_type'] == task_type and run['mission_success'] == 'TRUE')
        task_success_rate = task_success / count * 100 if count > 0 else 0
        print(f"{task_type.capitalize()}: {count} runs ({percentage:.1f}%) - {task_success_rate:.1f}% success rate")
    
    # Battery Analysis
    print("\n🔋 BATTERY ANALYSIS")
    print("-" * 40)
    
    # Battery consumption for successful missions
    battery_data = []
    for run in runs:
        if run['mission_success'] == 'TRUE' and run['battery_consumed'].isdigit():
            battery_data.append(int(run['battery_consumed']))
    
    if battery_data:
        avg_battery = sum(battery_data) / len(battery_data)
        min_battery = min(battery_data)
        max_battery = max(battery_data)
        print(f"Average Battery Consumption: {avg_battery:.1f}%")
        print(f"Battery Consumption Range: {min_battery}% - {max_battery}%")
    
    # Energy Efficiency Analysis
    efficiency_data = []
    for run in runs:
        if run['mission_success'] == 'TRUE' and run['energy_efficiency'].replace('.', '').isdigit():
            efficiency_data.append(float(run['energy_efficiency']))
    
    if efficiency_data:
        avg_efficiency = sum(efficiency_data) / len(efficiency_data)
        print(f"Average Energy Efficiency: {avg_efficiency:.1f} meters per 1% battery")
    
    # Bidding Score Analysis
    print("\n💰 BIDDING ANALYSIS")
    print("-" * 40)
    
    winning_scores = []
    winning_margins = []
    
    for run in runs:
        if run['winner_score'].replace('.', '').isdigit():
            winning_scores.append(float(run['winner_score']))
        if run['winning_margin'].replace('.', '').isdigit():
            winning_margins.append(float(run['winning_margin']))
    
    if winning_scores:
        avg_winning_score = sum(winning_scores) / len(winning_scores)
        print(f"Average Winning Bid Score: {avg_winning_score:.3f}")
    
    if winning_margins:
        avg_margin = sum(winning_margins) / len(winning_margins)
        print(f"Average Winning Margin: {avg_margin:.3f}")
        competitive_runs = sum(1 for margin in winning_margins if margin < 0.05)
        print(f"Competitive Runs (margin < 0.05): {competitive_runs} ({competitive_runs/len(winning_margins)*100:.1f}%)")
    
    # Specialization Impact Analysis
    print("\n🎯 SPECIALIZATION ANALYSIS")
    print("-" * 40)
    
    specialization_wins = 0
    total_specialization_opportunities = 0
    
    for run in runs:
        # Check if any agent had specialization bonus
        agents = ['uav1', 'uav2', 'uav3', 'uav4']
        for agent in agents:
            bonus_key = f"{agent}_specialization_bonus"
            if bonus_key in run and run[bonus_key] not in ['N/A', '0', '0.0']:
                total_specialization_opportunities += 1
                if run['winner_agent'] == agent:
                    specialization_wins += 1
                break
    
    if total_specialization_opportunities > 0:
        spec_win_rate = specialization_wins / total_specialization_opportunities * 100
        print(f"Specialization Win Rate: {specialization_wins}/{total_specialization_opportunities} ({spec_win_rate:.1f}%)")
    else:
        print("No specialization bonuses detected in data")
    
    # Elimination Reasons Analysis
    print("\n❌ ELIMINATION ANALYSIS")
    print("-" * 40)
    
    elimination_reasons = Counter()
    for run in runs:
        if run['elimination_reasons'] and run['elimination_reasons'] != 'none':
            reasons = run['elimination_reasons'].split('; ')
            for reason in reasons:
                if ':' in reason:
                    _, reason_type = reason.split(':', 1)
                    elimination_reasons[reason_type.strip()] += 1
    
    for reason, count in elimination_reasons.most_common():
        print(f"{reason}: {count} eliminations")
    
    # Performance Trends (if multiple runs)
    if total_runs >= 5:
        print("\n📈 PERFORMANCE TRENDS")
        print("-" * 40)
        
        # Group runs into early vs late
        mid_point = total_runs // 2
        early_runs = runs[:mid_point]
        late_runs = runs[mid_point:]
        
        early_success = sum(1 for run in early_runs if run['mission_success'] == 'TRUE') / len(early_runs) * 100
        late_success = sum(1 for run in late_runs if run['mission_success'] == 'TRUE') / len(late_runs) * 100
        
        print(f"Early Runs Success Rate: {early_success:.1f}%")
        print(f"Late Runs Success Rate: {late_success:.1f}%")
        print(f"Performance Trend: {'Improving' if late_success > early_success else 'Stable' if late_success == early_success else 'Declining'}")
    
    print("\n" + "=" * 80)
    print("ANALYSIS COMPLETE")
    print("=" * 80)
    
    # Recommendations
    print("\n💡 RECOMMENDATIONS FOR NEXT EXPERIMENTS:")
    if success_rate < 95:
        print("- Investigate mission failure causes")
    if total_eliminated / total_runs > 1:
        print("- Consider more realistic battery level distributions")
    if len(set(run['winner_agent'] for run in runs)) == 1:
        print("- Vary agent configurations to test different scenarios")
    print("- Continue collecting data to reach 50 total runs")
    print("- Consider running Experiment A2 (Sequential Tasks) next")

def export_for_analysis():
    """Export data in formats suitable for statistical analysis"""
    print("Exporting data for external analysis...")
    
    # TODO: Add export functions for R, MATLAB, etc.
    print("Feature coming soon: Export to R/MATLAB format")

if __name__ == "__main__":
    analyze_summary_data()
    print("\nFor detailed statistical analysis, use external tools with the CSV data.")
