# EZR Stability Analysis: analyze_ezr_stability.py

## Overview

`analyze_ezr_stability.py` runs **Explainable Rule Extraction (EZR)** multiple times on a dataset and analyzes **convergence and stability** of the resulting trees. Unlike the 3D Pareto analysis, this script focuses on:

- **2D Pareto frontier** (Accuracy vs. Complexity)
- **Feature consensus**: Which features appear consistently (≥80%)?
- **Feature exploration**: Which features are tried rarely (<40%)?
- **Convergence tracking**: How does the Pareto front stabilize over runs?

This tool is ideal for understanding whether EZR has found a stable, reproducible solution or if it's still exploring the feature space.

---

## Quick Comparison: 2D vs 3D Analysis

### `analyze_ezr_stability.py` (This Script)
- **Dimensions**: 2D (Accuracy × Complexity)
- **Focus**: Convergence, consensus features, stability over runs
- **Pareto Type**: Simple 2D dominance
- **Output**: CSV, JSON, Markdown report, PNG visualization
- **Use Case**: Understanding stability, finding consensus, exploring convergence behavior
- **Interval Checks**: Tracks stability at regular intervals (every N runs)

### `tree_pareto_3d.py` (Comparison)
- **Dimensions**: 3D (Accuracy × Simplicity × Stability)
- **Focus**: Multi-objective trade-off landscape
- **Pareto Type**: 3D dominance with feature frequency stability metric
- **Output**: CSV, JSON, 3D visualization, summary markdown
- **Use Case**: Stakeholder decision-making, trade-off visualization
- **No Interval Checks**: Single analysis after all runs

---

## What It Does

1. **Runs EZR N times** (typically 20-50 runs)
2. **Checks stability at intervals** (every 5, 10, or custom number of runs)
3. **For each checkpoint**, calculates:
   - Pareto frontier (non-dominated trees)
   - Consensus features (appear ≥80% of runs)
   - Exploratory features (appear <40% of runs)
   - Accuracy range on frontier
4. **Generates outputs**:
   - CSV files (trees, frontier, features, stability history)
   - JSON export (full data structure)
   - Human-readable report (Markdown)
   - Visualizations (2D Pareto plots)

---

## Dependencies

- **Python 3.7+**
- **EZR** (Explainable Rule Extraction) — must be installed and available as `ezr` command
- **pandas** — data manipulation
- **numpy** — numerical operations (optional)
- **matplotlib** — 2D visualization

### Installation

```bash
# Install Python dependencies
pip install pandas numpy matplotlib

# Ensure EZR is installed and in PATH
which ezr  # Should return path to EZR executable
```

---

## Usage

### Basic Usage

```bash
python3 analyze_ezr_stability.py \
  --runs 50 \
  --dataset /path/to/dataset.csv \
  --stability-check 5
```

### Command-Line Arguments

```
--runs N                 Number of EZR runs (default: 20)
--dataset PATH          Path to CSV dataset (required)
--stability-check N     Check stability every N runs (default: 5)
--output-dir DIR        Output directory (default: ezr_analysis)
```

### Examples

```bash
# Quick test: 20 runs, check stability every 5 runs
python3 analyze_ezr_stability.py \
  --runs 20 \
  --dataset my_data.csv \
  --stability-check 5

# Thorough analysis: 100 runs, check every 10 runs
python3 analyze_ezr_stability.py \
  --runs 100 \
  --dataset my_data.csv \
  --stability-check 10

# Aggressive: 200 runs, check every 25 runs
python3 analyze_ezr_stability.py \
  --runs 200 \
  --dataset my_data.csv \
  --stability-check 25
```

---

## Output Files

### CSV Files

#### `all_trees.csv`
All generated trees with metrics:
```
run_num,features,complexity,win,on_frontier
1,"income_Category, education_Level",2,75,True
2,"income_Category, marital_Status",2,68,False
3,"income_Category, card_Category, education_Level",3,72,True
```

Columns:
- `run_num`: Which run (1-50)
- `features`: Comma-separated feature names
- `complexity`: Number of features
- `win`: Accuracy percentage
- `on_frontier`: Boolean, is this tree Pareto-optimal?

#### `feature_frequency.csv`
How often each feature appears:
```
feature,occurrences,frequency_%,appears_in_frontier_%
income_Category,45,90.0,100.0
education_Level,35,70.0,85.7
marital_Status,24,48.0,50.0
```

Columns:
- `feature`: Feature name
- `occurrences`: Count across all runs
- `frequency_%`: Percentage of all runs
- `appears_in_frontier_%`: Percentage of frontier trees

#### `pareto_front.csv`
Pareto-optimal (non-dominated) trees:
```
run_num,features,complexity,win
1,"income_Category, education_Level",2,75
3,"income_Category, card_Category, education_Level",3,72
5,"income_Category, marital_Status, card_Category",3,78
```

#### `stability_analysis.csv`
Convergence history (one row per stability check):
```
checkpoint_run,pareto_front_size,num_consensus_features,num_exploratory_features,accuracy_min,accuracy_max
5,3,1,12,68,75
10,4,2,10,65,78
15,4,2,8,64,79
20,5,3,6,62,80
```

Columns:
- `checkpoint_run`: Which run was this check done at?
- `pareto_front_size`: How many non-dominated trees?
- `num_consensus_features`: Features appearing ≥80%
- `num_exploratory_features`: Features appearing <40%
- `accuracy_min/max`: Range on current frontier

### Markdown & Text Files

#### `summary_report.md`
Human-readable summary with:
- Overview of all runs
- Final Pareto front with annotations
- Consensus features (≥80%)
- Exploratory features (<40%)
- Convergence narrative
- Key insights

#### `results_detailed.txt`
Detailed text export with:
- Full tree listing
- Feature frequency table
- Stability checkpoint details
- Formatted for readability

### JSON & Visualization

#### `results.json`
Complete data structure (all trees, features, stability history) in JSON format.

#### `pareto_front.png`
2D Pareto visualization:
- **X-axis**: Complexity (# features)
- **Y-axis**: Accuracy (%)
- **Points**: Individual trees
- **Frontier**: Highlighted in color
- **Zones**: Safe (simple), Risky (complex)

#### `pareto_front_detailed.png`
Same as above but with annotations for each frontier tree.

---

## Understanding the Analysis

### 2D Pareto Frontier

A tree is **Pareto-optimal** if no other tree has:
- **Higher accuracy** AND **lower complexity** (simpler)

In other words, you can't improve accuracy without adding features (complexity).

```
Frontier trees: You must choose a trade-off
Off-frontier: Strictly dominated by some frontier tree
```

### Consensus vs. Exploratory Features

**Consensus Features (≥80%)**
- Appear in 80%+ of all runs
- EZR reliably selects these
- Core predictive signal
- Safe to depend on

**Exploratory Features (<40%)**
- Appear in <40% of runs
- EZR tries these occasionally
- Not essential
- May be noise or context-dependent

**Middle Ground (40-80%)**
- Moderately important
- Selected sometimes, not always
- Supporting signal

---

## Interpreting Convergence

### Stability Checkpoint Output

```
[Run 5] 📈 Stability check at run 5...
  Pareto Front Size: 3
  Accuracy Range: (68, 75)
  Consensus Features (≥80%): 1
    • income_Category: 100.0%
  Exploratory Features (<40%): 12
    • marital_Status: 20.0%
    • card_Category: 20.0%
    ...

[Run 10] 📈 Stability check at run 10...
  Pareto Front Size: 4
  Accuracy Range: (65, 78)
  Consensus Features (≥80%): 2
    • income_Category: 100.0%
    • education_Level: 80.0%
  Exploratory Features (<40%): 10
    ...

[Run 15] 📈 Stability check at run 15...
  Pareto Front Size: 5
  Accuracy Range: (64, 79)
  Consensus Features (≥80%): 2
    • income_Category: 100.0%
    • education_Level: 86.7%
  Exploratory Features (<40%): 8
    ...
```

**Interpretation**: The frontier is growing (3 → 4 → 5 trees), consensus features are stable (income always 100%), exploratory features shrinking (12 → 10 → 8). This suggests **convergence** — the algorithm is settling on reliable solutions.

### Convergence Patterns

**Pattern 1: Fast Convergence ✅**
```
Runs 0-10:   Frontier grows (2→3→4), consensus builds
Runs 10-20:  Frontier stabilizes (4→4→4), features lock in
Interpretation: Solution found early, very stable
```

**Pattern 2: Gradual Convergence ✅**
```
Runs 0-20:   Frontier grows steadily (2→3→4→5), consensus builds slowly
Runs 20-50:  Frontier stabilizes (5→5→5), consensus complete
Interpretation: Algorithm exploring carefully, finding good solution
```

**Pattern 3: No Convergence ⚠️**
```
Runs 0-50:   Frontier keeps growing (2→5→8→10), features never stabilize
Interpretation: Algorithm still exploring, no clear winner, more runs needed
```

---

## Workflow Example

### Step 1: Run Analysis

```bash
python3 analyze_ezr_stability.py \
  --runs 50 \
  --dataset BankChurners.csv \
  --stability-check 5
```

Output during runs:
```
🚀 Starting EZR analysis: 50 runs with stability check every 5 runs
📊 Dataset: BankChurners.csv
💾 Output directory: ezr_analysis

[Run 1/50] Running EZR...
  ✓ Features: income_Category, education_Level
  ✓ Accuracy (win): 75
  ✓ Complexity: 2
...

[Run 5/50] Running EZR...
  ✓ Features: income_Category, marital_Status, card_Category
  ✓ Accuracy (win): 74
  ✓ Complexity: 3

📈 Stability check at run 5...
  Pareto Front Size: 3
  Accuracy Range: (68, 75)
  Consensus Features (≥80%): 1
    • income_Category: 100.0%
  Exploratory Features (<40%): 8

[Run 10/50] Running EZR...
...
```

### Step 2: Review Outputs

```bash
ls -la ezr_analysis/

# Quick overview
cat ezr_analysis/summary_report.md

# Check frontier stability over time
cat ezr_analysis/stability_analysis.csv

# See which features matter
cat ezr_analysis/feature_frequency.csv | head -10
```

### Step 3: Visualize

```bash
# View the 2D Pareto front
open ezr_analysis/pareto_front_detailed.png
```

You should see:
- Points scattered in accuracy vs. complexity space
- Frontier trees connected by a line
- Clear trade-off visualization
- Zones labeled (safe, risky, frontier)

### Step 4: Make Decision

```bash
# Which trees are on the frontier?
cat ezr_analysis/pareto_front.csv

# What features appear consistently?
cat ezr_analysis/feature_frequency.csv | grep "100.0"

# Decisions:
# - Simple + stable? Use 2-feature tree from frontier
# - High accuracy? Use complex tree from frontier
# - Balanced? Pick middle of frontier
```

---

## Key Metrics

### Pareto Front Size
- **Small (2-3)**: Strong consensus, few viable options
- **Medium (4-6)**: Good exploration, multiple valid choices
- **Large (>7)**: Too much variation, more runs needed

### Consensus Features
- **0 features**: No consensus (problematic)
- **1-2 features**: Clear core signal (good)
- **3+ features**: Essential base (very good)

### Exploratory Features
- **Shrinking over time**: Convergence (good)
- **Stable high count**: Still exploring (need more runs)
- **Few (<5)**: Focused exploration (excellent)

### Accuracy Range on Frontier
- **Narrow (e.g., 75-78%)**: Tightly constrained problem
- **Wide (e.g., 60-85%)**: Many valid solutions exist

---

## Customization

### Changing Stability Check Interval

More frequent checks = more granular convergence tracking, slower script:

```bash
# Check every 1 run (very detailed)
python3 analyze_ezr_stability.py --runs 50 --stability-check 1

# Check every 10 runs (less detailed)
python3 analyze_ezr_stability.py --runs 50 --stability-check 10
```

### Changing Consensus/Exploratory Thresholds

Edit the script (around line 175):

```python
# Current thresholds:
consensus_features = {f: pct for f, pct in feature_pcts.items() if pct >= 80}
exploratory_features = {f: pct for f, pct in feature_pcts.items() if pct < 40}

# Custom example: 70%+ for consensus, 30%+ for exploratory
consensus_features = {f: pct for f, pct in feature_pcts.items() if pct >= 70}
exploratory_features = {f: pct for f, pct in feature_pcts.items() if pct < 30}
```

### Changing Output Directory

```bash
python3 analyze_ezr_stability.py \
  --runs 50 \
  --dataset data.csv \
  --output-dir my_results/
```

---

## FAQ

**Q: How many runs do I need?**  
A: Start with 20 runs. If frontier still growing, run 50. If still unstable, run 100+.

**Q: What's a "good" Pareto front size?**  
A: 4-6 trees indicates a well-explored problem. <3 suggests limited exploration; >10 suggests instability.

**Q: Why does my consensus feature list change between checkpoints?**  
A: Because the percentage keeps updating as you run more iterations. This is normal. Watch for stabilization.

**Q: Can I combine results from multiple runs?**  
A: Yes, all trees get added to `all_trees.csv`. Re-run with `--stability-check` at different intervals for new checkpoints.

**Q: What if no features reach 80% consensus?**  
A: This means the problem is inherently exploratory. The features matter, but EZR tries different combinations. Run more iterations or investigate data quality.

**Q: How does this differ from the 3D analysis?**  
A: This script focuses on **convergence over time** with **checkpoint tracking**. The 3D script focuses on **multi-objective optimization** with **feature frequency stability metric**. Use this for stability questions; use 3D for stakeholder trade-off decisions.

**Q: Can I use the Pareto front from here in production?**  
A: Yes! Pick a frontier tree based on your priority:
- Want simple? Pick the tree with fewest features on frontier
- Want accurate? Pick the tree with highest win score on frontier
- Want balanced? Pick the middle tree on frontier

---

## Example: Full Workflow

```bash
# 1. Run 50 iterations with checkpoint every 5 runs
python3 analyze_ezr_stability.py \
  --runs 50 \
  --dataset BankChurners.csv \
  --stability-check 5

# 2. Review summary
cat ezr_analysis/summary_report.md | less

# 3. Check feature consensus
grep "100.0" ezr_analysis/feature_frequency.csv
# Output: income_Category appears in 100% of runs → CORE FEATURE

# 4. Check convergence history
cat ezr_analysis/stability_analysis.csv
# If pareto_front_size stays same after run 25, it's converged

# 5. Get frontier trees
cat ezr_analysis/pareto_front.csv

# 6. Decide which to use
# Option A: Simplicity → pick 2-feature tree
# Option B: Accuracy → pick highest-win tree
# Option C: Balance → pick middle of frontier
# Option D: Consensus → pick tree using income_Category (100%)

# 7. Implement chosen tree
# Use run number to look up full tree in results.json
```

---

## Performance Notes

- **Runtime**: ~30 seconds per run + checkpoint analysis overhead
  - 50 runs: ~25-30 minutes total
  - Stability checks add ~1-2 seconds per checkpoint
- **Memory**: Minimal (all data fits in RAM)
- **Disk**: ~3-5 MB output (mostly CSVs + JSON)

---

## Troubleshooting

### Error: `ezr: command not found`
```bash
which ezr  # Check if installed
# If not found, install EZR and add to PATH
```

### Error: `FileNotFoundError: dataset.csv`
```bash
# Use absolute path
python3 analyze_ezr_stability.py \
  --dataset ~/gits/moot/optimize/financial_data/BankChurners.csv
```

### Error: `Empty pareto front`
**Cause**: No valid trees extracted  
**Solution**: Check dataset format, increase `--runs`, verify EZR works directly

### Pareto front size keeps growing
**Cause**: Algorithm still exploring, no convergence yet  
**Solution**: Increase `--runs` to 100+, check feature frequency for consensus

---

## Citation & References

This tool implements:
- **2D Pareto optimization** for decision trees
- **Convergence analysis** through checkpoint tracking
- **Consensus/exploratory feature categorization**
- **Tree dominance** based on accuracy and complexity

---

## Support

For issues:
1. Check **Troubleshooting** section above
2. Inspect output CSVs for clues
3. Look at `stability_analysis.csv` for convergence history
4. Check `summary_report.md` for analysis narrative

---

*Generated by: analyze_ezr_stability.py | Last updated: April 2025*
