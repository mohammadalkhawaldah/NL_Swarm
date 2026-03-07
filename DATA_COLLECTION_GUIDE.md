# Experiment A1 Data Collection Workflow

## Files Overview

1. **`experiment_A1_summary.csv`** - Master summary file with one row per experimental run
2. **`add_experiment_data.py`** - Interactive tool to add new runs to the summary
3. **`comprehensive_analysis.py`** - Analysis script to generate statistics and insights
4. **`experiment_A1_run_XXX.csv`** - Detailed logs for individual runs (optional)

## Quick Workflow After Each Experiment

### Step 1: Run Your Experiment
```bash
# Terminal 1: Start agents
python D1_agent_new.py
python D2_agent_new.py  
python D3_agent_new.py
python D4_agent_new.py

# Terminal 2: Send task
python task_extract_send_rdp.py
```

### Step 2: Collect Data
```bash
# Run the interactive data collection tool
python add_experiment_data.py
```

### Step 3: Analyze Results
```bash
# View comprehensive analysis
python comprehensive_analysis.py
```

## Data Collection Tips

### Before Each Run:
- [ ] Plan battery levels for each agent
- [ ] Decide on task type (delivery/survey/patrol/emergency)
- [ ] Choose target location
- [ ] Note any special conditions

### During the Run:
- [ ] Save all agent terminal outputs
- [ ] Note exact timestamps
- [ ] Record any unusual behaviors

### After the Run:
- [ ] Fill out summary CSV using the tool
- [ ] Run analysis script
- [ ] Save agent logs (optional detailed records)

## Variations to Test (Experiment A1 - 50 runs total)

### Battery Level Combinations:
- Run 002: [100%, 40%, 80%, 60%] - Test low battery impact
- Run 003: [80%, 20%, 100%, 40%] - Test very low battery
- Run 004: [60%, 60%, 60%, 60%] - Equal battery levels
- Run 005: [100%, 100%, 100%, 0%] - Test single elimination

### Task Types:
- Runs 006-015: Delivery tasks (test uav2 specialization)
- Runs 016-025: Survey tasks (test uav1 specialization) 
- Runs 026-035: Patrol tasks (test uav3 specialization)
- Runs 036-045: Emergency tasks (test high priority)
- Runs 046-050: Mixed types

### Distance Variations:
- Close targets (< 1km)
- Medium targets (1-3km)
- Far targets (> 3km)
- Different directions (N/S/E/W)

### Agent Position Variations:
- Clustered start positions
- Spread out positions
- Linear arrangements
- Different home base locations

## Analysis Metrics to Track

### Key Performance Indicators:
- Mission success rate (target: >95%)
- Winner distribution fairness
- Battery consumption efficiency
- Bidding competitiveness (close scores)
- Specialization effectiveness

### Red Flags to Watch:
- Single agent winning too often (>60%)
- High elimination rates (>50%)
- Mission failures
- Very uncompetitive bidding (margins >0.1)
- System crashes or communication failures

## Sample Commands

```bash
# Quick analysis of current data
python comprehensive_analysis.py

# Add new experimental run interactively  
python add_experiment_data.py

# View just the summary statistics
python add_experiment_data.py  # Choose option 2
```

## Export for Statistical Analysis

The CSV file can be imported into:
- **Python pandas** for detailed analysis
- **R** for statistical modeling
- **Excel** for charts and pivot tables
- **MATLAB** for advanced analysis
- **SPSS** for statistical tests

## Research Paper Data

This systematic data collection will provide:
- 50 experimental runs for statistical significance
- Comparative analysis across conditions
- Performance benchmarks
- Validation of algorithm effectiveness
- Publication-quality datasets

## Next Experiments

After completing 50 runs of A1:
- **Experiment A2**: Multiple tasks, sequential
- **Experiment A3**: Concurrent task competition  
- **Experiment B1**: Network delay simulation
- **Experiment C1**: Agent count scaling
