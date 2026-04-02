# EZR Stability Analysis Script - Usage Guide

## Quick Start

### Installation

```bash
# Make the script executable
chmod +x analyze_ezr_stability.py

# Install dependencies (if not already installed)
pip install pandas

# Ensure EZR is installed and accessible
which ezr
```

### Basic Usage

```bash
# Run 20 times with stability checks every 5 runs
python3 analyze_ezr_stability.py \
  --runs 20 \
  --dataset ~/gits/moot/optimize/financial_data/BankChurners.csv

# Output goes to: ezr_analysis/ directory
```

### Common Use Cases

#### For Preliminary Results (10 runs)
```bash
python3 analyze_ezr_stability.py \
  --runs 10 \
  --dataset ~/gits/moot/optimize/financial_data/BankChurners.csv \
  --stability-check 5
```

#### For Full Paper (30 runs)
```bash
python3 analyze_ezr_stability.py \
  --runs 30 \
  --dataset ~/gits/moot/optimize/financial_data/BankChurners.csv \
  --stability-check 5
```

#### For Custom Output Directory
```bash
python3 analyze_ezr_stability.py \
  --runs 20 \
  --dataset ~/gits/moot/optimize/financial_data/BankChurners.csv \
  --stability-check 5 \
  --output-dir ./my_analysis
```

---

## Visualization Output

The script also generates **two high-quality Pareto front visualizations**:

### 1. `pareto_front.png` - Simple Overview
Clean, simple visualization showing:
- **Green dots**: Trees on the Pareto frontier
- **Gray dots**: Off-frontier trees (dominated)
- **Red star**: The "knee" point (optimal trade-off)
- **Green dashed line**: Frontier path

**Use this for:** Presentations, reports, quick overview

### 2. `pareto_front_detailed.png` - Detailed Analysis
Advanced visualization with:
- Run numbers labeled on each point
- Knee point highlighted with annotation
- Frontier path highlighted
- Summary statistics box
- Full details visible

**Use this for:** Papers, detailed analysis, publication

---

## What The Script Does

### 1. Runs EZR Automatically
- Executes `ezr -f <dataset>` the specified number of times
- Each run generates a different decision tree (due to random initialization)
- Captures all output for parsing

### 2. Parses Output
Extracts from each run:
- **Features**: Which variables the tree uses
- **Accuracy (win)**: Performance score
- **Complexity**: Number of features

### 3. Checks Stability at Regular Intervals
Every N runs (default: 5), analyzes:
- **Pareto Front Size**: How many trees are on the frontier
- **Feature Frequency**: How often each feature appears
- **Consensus Features**: Which features appear ≥80% of the time
- **Exploratory Features**: Which appear <40% of the time
- **Accuracy Range**: Min/max performance on frontier

### 4. Generates 9 Output Files

```
ezr_analysis/
├── all_trees.csv                    # All generated trees
├── feature_frequency.csv            # Feature usage analysis  
├── pareto_front.csv                 # Frontier trees only
├── stability_analysis.csv           # Convergence tracking
├── summary_report.md                # Executive summary (MD format)
├── results_detailed.txt             # All data in text format
├── results.json                     # All data in JSON
├── pareto_front.png                 # Simple visualization (300 dpi)
└── pareto_front_detailed.png        # Detailed visualization with labels (300 dpi)
```

---

## Output Files Explained

### 1. `all_trees.csv`
Complete list of all generated trees.

```csv
run_num,features,complexity,win,on_frontier
1,"income_Category, card_Category, Contacts_Count_12_mon",3,68,true
2,"education_Level, income_Category, card_Category",3,64,true
3,"education_Level, marital_Status, income_Category, Total_Trans_Ct, Avg_Utilization_Ratio",5,65,false
...
```

**Columns:**
- `run_num`: Which run (1-20)
- `features`: Feature names (comma-separated)
- `complexity`: Number of features
- `win`: Accuracy score
- `on_frontier`: Is this tree on the Pareto frontier?

---

### 2. `feature_frequency.csv`
How often each feature appears across all runs.

```csv
feature,count,runs,frequency_%,classification
income_Category,20,20,100.0%,CONSENSUS
marital_Status,16,20,80.0%,IMPORTANT
education_Level,14,20,70.0%,IMPORTANT
card_Category,12,20,60.0%,UNCERTAIN
Total_Trans_Ct,6,20,30.0%,EXPLORATORY
CLIENTNUM,2,20,10.0%,EXPLORATORY
```

**Classifications:**
- `CONSENSUS`: ≥80% - These features are reliable
- `IMPORTANT`: 60-80% - Often appear, but not guaranteed
- `UNCERTAIN`: 40-60% - Appear sometimes
- `EXPLORATORY`: <40% - Rare, likely dataset artifacts

---

### 3. `pareto_front.csv`
Only trees that are on the Pareto frontier (not dominated on both accuracy AND complexity).

```csv
run_num,features,complexity,win,on_knee
1,"income_Category, card_Category, Contacts_Count_12_mon",3,68,true
8,"income_Category, card_Category, contacts_count",3,67,false
10,"income_Category, card_Category, Contacts_Count_12_mon",3,69,false
```

**Key insight:** All frontier trees use 3 features (the minimum). This is the "knee of the curve."

---

### 4. `stability_analysis.csv`
Tracks convergence across runs.

```csv
run_num,pareto_front_size,num_consensus_features,num_exploratory_features,accuracy_min,accuracy_max
5,3,1,4,66,68
10,4,2,3,66,70
15,5,3,2,66,71
20,5,3,2,66,71
```

**How to read:**
- At run 5: 3 trees on frontier, 1 consensus feature, accuracy ranges 66-68
- At run 10: 4 trees on frontier (still growing)
- At run 15: 5 trees (stable, same at run 20)
- At run 20: **STABLE** - frontier not growing, features not changing

When pareto_front_size stops growing, you have enough data.

---

### 5. `summary_report.md`
Human-readable markdown report. Contains:
- Executive summary
- Consensus features with %
- Important/exploratory features
- Pareto front analysis
- Knee of curve identification
- Stability assessment
- Recommendations

**This is the one to read first!**

---

### 6. `results_detailed.txt` (NEW!)
Comprehensive human-readable text export of all results.

```
================================================================================
EZR STABILITY ANALYSIS - DETAILED RESULTS
================================================================================

1. ALL GENERATED TREES (20 trees)
   Run 1: ✓ ON FRONTIER
     Features (3): income_Category, card_Category, Contacts_Count_12_mon
     Accuracy (win): 68
   
   Run 2: off frontier
     Features (3): education_Level, income_Category, card_Category
     Accuracy (win): 64
   ...

2. FEATURE FREQUENCY ANALYSIS
   
   CONSENSUS FEATURES (≥80% of runs)
     income_Category                      20/20  100.0%
     marital_Status                       16/20   80.0%
   
   IMPORTANT FEATURES (60-80% of runs)
     education_Level                      14/20   70.0%
   
   EXPLORATORY FEATURES (<40% of runs)
     CLIENTNUM                             2/20   10.0%
     contacts_count                        2/20   10.0%

3. PARETO FRONT (4 trees on frontier)
   
   1. Run 10 ← KNEE OF CURVE
      Features (3): income_Category, card_Category, Contacts_Count_12_mon
      Accuracy: 69
   
   2. Run 1
      Features (3): income_Category, card_Category, Contacts_Count_12_mon
      Accuracy: 68
   ...

4. STABILITY HISTORY (Convergence tracking)
   
   Run #  │ Frontier Size │ Consensus Feat │ Exploratory │ Accuracy Range
   ────────────────────────────────────────────────────────────────────────
      5  │       2       │       1        │      4      │  66-68
     10  │       3       │       2        │      3      │  66-70
     15  │       4       │       2        │      3      │  66-71
     20  │       4       │       2        │      3      │  66-71

5. SUMMARY STATISTICS
   ACCURACY: Min 64, Max 69, Mean 67.0
   COMPLEXITY: Min 3, Max 5
   ...

6. CONVERGENCE ASSESSMENT
   ✓ STABLE - Frontier size 4 unchanged since run 15
   ✓ STABLE - 2 consensus features unchanged
```

**This file has everything you need, formatted nicely for reading in a text editor.**

---

### 7. `pareto_front.png` (NEW!)
Simple Pareto front visualization (300 dpi, publication quality).

**What you see:**
- 🟢 **Green dots**: Trees on the Pareto frontier (optimal)
- ⚫ **Gray dots**: Off-frontier trees (dominated)
- 🟥 **Red star**: The "knee" point (best trade-off)
- 🟩 **Green dashed line**: Path along the frontier

**Perfect for:**
- Presentations
- Quick overview
- Papers that need simple visuals
- Reports

---

### 8. `pareto_front_detailed.png` (NEW!)
Detailed Pareto front with full annotations (300 dpi, publication quality).

**What you see:**
- Each point labeled with its run number (e.g., "Run 5")
- Knee point prominently highlighted with annotation box
- Summary statistics in top-left corner
- Frontier path shown
- All details visible at a glance

**Perfect for:**
- Detailed analysis
- Publications requiring full documentation
- Presentations where you need to point out specific models
- Papers with space for larger figures

---
All data in JSON format for programmatic access.

```json
{
  "metadata": {
    "generated": "2026-04-01T12:34:56.789012",
    "dataset": "~/gits/moot/optimize/financial_data/BankChurners.csv",
    "total_runs": 20
  },
  "all_trees": [...],
  "feature_frequency": {
    "features": {"income_Category": 20, ...},
    "percentages": {"income_Category": 100.0, ...},
    "consensus": {"income_Category": 100.0, ...},
    "important": {...},
    "exploratory": {...}
  },
  "pareto_front": [...],
  "stability_history": [...]
}
```

Use this if you want to:
- Import data into other tools
- Build custom visualizations
- Programmatic access to results

---

## Interpreting the Pareto Front Visualizations

### What the Visualizations Show

The Pareto front plot displays the trade-off between two objectives:
- **X-axis (Horizontal)**: Complexity = number of features in the decision tree
- **Y-axis (Vertical)**: Accuracy = win score (performance metric)

### Understanding the Points

**Green points on the frontier:**
- These models are "Pareto optimal"
- No other model beats them on BOTH accuracy AND simplicity
- You should consider these for your final decision

**Gray points off the frontier:**
- These models are "dominated"
- There's at least one green point that's better on both dimensions
- Example: Tree with 5 features and 65 accuracy is dominated by a tree with 3 features and 68 accuracy
- Safe to ignore these

**Red star (the knee):**
- This is the "sweet spot" of the Pareto frontier
- It's at the point of diminishing returns
- Adding more features beyond here doesn't significantly improve accuracy
- This is usually the best choice for production

### Reading the Example

```
If you see:

Accuracy
   70 |          ✓ (Knee: 3 feat, 70 acc)
   65 |     ✓ X (5 feat, 65 acc - dominated)
       |    ✓ ✓ (frontier)
   60 |
      +---+---+---+---+---+
       1   2   3   4   5
          Complexity

This means:
- The knee point (red star) has 3 features and 70 accuracy
- Tree X (gray) has 5 features but LOWER accuracy (65) - avoid this
- All the green points are worth considering
- But the knee is usually the best choice
```

---

## Using the Visualizations in Your Research

### For Presentations
```bash
# Use the simple version
cp ezr_analysis/pareto_front.png my_presentation/

# Easy to explain: "Green dots are good, gray dots are bad, red star is the best"
```

### For Papers
```bash
# Use the detailed version with run numbers
cp ezr_analysis/pareto_front_detailed.png paper_figures/

# Include caption:
# "Figure X: Pareto front showing accuracy vs. complexity trade-off.
#  Green dots represent frontier models (Pareto optimal).
#  Red star indicates the knee point (optimal efficiency).
#  Gray dots represent dominated models."
```

### For Analysis
```bash
# Open both images side-by-side
# Simple version for quick understanding
# Detailed version for identifying specific trees

# Cross-reference with pareto_front.csv to get exact feature lists
cat ezr_analysis/pareto_front.csv
```

---
```
CONSENSUS FEATURES (≥80%):
- income_Category: 100%
- marital_Status: 85%

EXPLORATORY FEATURES (<40%):
- CLIENTNUM: 10%
- education_Level_Unknown: 5%
```

**Interpretation:** income and marital status are RELIABLE. CLIENTNUM is noise.

---

### Example 2: Pareto Front Stabilizes Early (GOOD)
```
Run 5:  Pareto front = 2 trees
Run 10: Pareto front = 3 trees
Run 15: Pareto front = 3 trees ← STABLE
Run 20: Pareto front = 3 trees ← STABLE
```

**Interpretation:** After 10 runs, you had enough data. Could have stopped there.

---

### Example 3: Frontier Still Growing (NEED MORE RUNS)
```
Run 5:  Pareto front = 3 trees
Run 10: Pareto front = 5 trees
Run 15: Pareto front = 7 trees
Run 20: Pareto front = 9 trees ← STILL GROWING
```

**Interpretation:** Run more to stabilize.

---

### Example 4: No Clear Consensus (UNCERTAIN)
```
CONSENSUS FEATURES: None (nothing ≥80%)
IMPORTANT FEATURES: Many (lots at 60-80%)
EXPLORATORY FEATURES: Many (lots <40%)
```

**Interpretation:** The optimization landscape is diverse. Run more to find true signals.

---

## Step-by-Step Example: Your BankChurners Data

### Step 1: Run for Preliminary Results
```bash
cd ~/your_project
python3 analyze_ezr_stability.py \
  --runs 15 \
  --dataset ~/gits/moot/optimize/financial_data/BankChurners.csv
```

**Expected output:**
```
🚀 Starting EZR analysis: 15 runs with stability check every 5 runs
📊 Dataset: ~/gits/moot/optimize/financial_data/BankChurners.csv
💾 Output directory: ezr_analysis

[Run 1/15] Running EZR...
  ✓ Features: income_Category, card_Category, Contacts_Count_12_mon
  ✓ Accuracy (win): 68
  ✓ Complexity: 3

[Run 2/15] Running EZR...
  ✓ Features: education_Level, income_Category, card_Category
  ✓ Accuracy (win): 64
  ✓ Complexity: 3

...

📈 Stability check at run 5...
  Pareto Front Size: 2
  Accuracy Range: (66, 68)
  Consensus Features (≥80%): 2
    • income_Category: 100.0%
    • card_Category: 80.0%
  Exploratory Features (<40%): 2
    • CLIENTNUM: 20.0%
    • contacts_count: 20.0%

...

✅ Completed 15 successful runs

💾 Generating output files...
  ✓ all_trees.csv
  ✓ feature_frequency.csv
  ✓ pareto_front.csv
  ✓ stability_analysis.csv
  ✓ summary_report.md
  ✓ results_detailed.txt
  ✓ results.json
  ✓ pareto_front.png ← NEW! Simple visualization
  ✓ pareto_front_detailed.png ← NEW! Detailed visualization

📂 All files saved to: ezr_analysis/

✨ Analysis complete!
📊 View results in: ezr_analysis/
📖 Start with: ezr_analysis/results_detailed.txt
📈 View visualizations: ezr_analysis/pareto_front.png
```

### Step 2: Read the Report
```bash
cat ezr_analysis/summary_report.md
```

You'll see:
- Executive summary
- Consensus features: income_Category (100%), marital_Status (80%)
- Exploratory features: CLIENTNUM (10%)
- Pareto front analysis
- Recommendation: "Use consensus features for production"

### Step 3: Examine Detailed Data
```bash
# View ALL data in human-readable format
cat ezr_analysis/results_detailed.txt

# Or view specific CSVs
cat ezr_analysis/feature_frequency.csv
cat ezr_analysis/all_trees.csv
cat ezr_analysis/pareto_front.csv
```

### Step 4: Check Stability
```bash
cat ezr_analysis/stability_analysis.csv
```

Look at the "pareto_front_size" column:
- If it's stable (same for last 2 checks) → You're done
- If it's still growing → Run more

---

## Integration with Your Study

### For Your Preliminary Results (Day 1)

```bash
# Generate consensus features and Pareto front
python3 analyze_ezr_stability.py \
  --runs 15 \
  --dataset ~/gits/moot/optimize/financial_data/BankChurners.csv \
  --output-dir ./preliminary_analysis

# Use outputs:
# - summary_report.md: Share with Tim
# - pareto_front.csv: Trees for Tier 1 evaluation
# - feature_frequency.csv: Document consensus features
```

### For Your April 20 Paper

```bash
# Generate publication-quality analysis
python3 analyze_ezr_stability.py \
  --runs 30 \
  --dataset ~/gits/moot/optimize/financial_data/BankChurners.csv \
  --output-dir ./paper_analysis

# Use outputs:
# - summary_report.md: Methods section + results
# - pareto_front.csv: Table of frontier models
# - feature_frequency.csv: Consensus analysis
# - results.json: Supplement data for paper
```

---

## Troubleshooting

### "ezr: command not found"
```bash
# Check if EZR is installed
which ezr

# If not, install it (from MOOT repo)
cd ~/gits/moot
python3 setup.py install

# Or try running ezr from repo directly
# Edit script to use full path to ezr
```

### "Error parsing EZR output"
The script may need adjustment for different EZR output formats. Edit the `parse_ezr_output()` method if you're using a different version.

### "Some runs failed/skipped"
This is normal. EZR sometimes fails on certain seeds. The script continues and reports successful runs. If >20% of runs fail, check:
1. Dataset integrity
2. Enough memory/CPU
3. EZR version compatibility

### Slow execution
- EZR itself is slow (minutes per run)
- 20 runs = ~40-60 minutes
- 30 runs = ~60-90 minutes
- This is normal

---

## Advanced: Customizing the Script

### Change Feature Thresholds
```python
# In the script, find this section:
if pct >= 80:
    classification = 'CONSENSUS'
elif pct >= 60:
    classification = 'IMPORTANT'

# Change 80 and 60 to your thresholds
if pct >= 75:  # Lower threshold
    classification = 'CONSENSUS'
elif pct >= 50:
    classification = 'IMPORTANT'
```

### Change Pareto Definition
The script uses: "Tree A dominates Tree B if A has better/equal accuracy AND fewer/equal features"

To use different objectives:
```python
# In identify_pareto_front(), modify the dominance check
# Current: accuracy AND complexity
# Alternative: accuracy AND training_time AND complexity

better_or_equal_accuracy = other['win'] >= tree['win']
simpler_or_equal = other['complexity'] <= tree['complexity']
faster = other['time'] <= tree['time']  # Add new objective

if better_or_equal_accuracy and simpler_or_equal and faster:
    # Dominate condition
```

### Export to Excel
```bash
# Convert CSV to Excel
pip install openpyxl

python3 << 'EOF'
import pandas as pd

# Read CSVs
trees = pd.read_csv('ezr_analysis/all_trees.csv')
features = pd.read_csv('ezr_analysis/feature_frequency.csv')
frontier = pd.read_csv('ezr_analysis/pareto_front.csv')
stability = pd.read_csv('ezr_analysis/stability_analysis.csv')

# Write to Excel with multiple sheets
with pd.ExcelWriter('ezr_analysis/results.xlsx') as writer:
    trees.to_excel(writer, sheet_name='All Trees', index=False)
    features.to_excel(writer, sheet_name='Feature Frequency', index=False)
    frontier.to_excel(writer, sheet_name='Pareto Front', index=False)
    stability.to_excel(writer, sheet_name='Stability', index=False)

print("✅ Exported to ezr_analysis/results.xlsx")
EOF
```

---

## Next Steps After Running

1. **Read** `summary_report.md` - Understand your findings
2. **Read** `results_detailed.txt` - All data in nice readable format ← START HERE
3. **Examine** `feature_frequency.csv` - Which features matter?
4. **Analyze** `pareto_front.csv` - What's the optimal model?
5. **Check** `stability_analysis.csv` - Do you have enough runs?
6. **Use** the frontier trees in your 3-tier evaluation (Tier 1)
7. **Report** consensus features in your paper

---

## Questions?

If the script doesn't work or you need customizations, check:
1. EZR is installed and callable
2. Dataset path is correct and file exists
3. You have pandas installed
4. You have write permissions in the output directory

Good luck! 🚀
