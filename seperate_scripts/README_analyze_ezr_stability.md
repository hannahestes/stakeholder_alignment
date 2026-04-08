# EZR 2D and 3D Pareto Stability Analysis

## Quick Comparison: 2D vs 3D Analysis

### `analyze_ezr_stability.py`
- **Dimensions**: 2D (Accuracy × Complexity)

### `tree_pareto_3d.py` (Comparison)
- **Dimensions**: 3D (Accuracy × Simplicity × Stability)

---

## What It Does

1. **Runs EZR N times** (we do 50 runs)
3. **For each entire run**, this calculates:
   - Pareto frontier (dominated trees)
   - Consensus features (appear ≥80% of runs)
   - Exploratory features (appear <40% of runs)
   - Accuracy range on frontier
4. **Generates outputs**:
   - CSV files (trees, frontier, features, stability history)
   - JSON export (full data structure)
   - Visualizations (2D and 3D Pareto-based plots)

---

## Dependencies

- **Python 3.7+**
- **EZR** (Explainable Rule Extraction) — must be installed and available as `ezr` command
- **pandas** — data manipulation
- **matplotlib** — 2D visualization
- **pathlib** — file path handling (3D only)

### Installation

```bash
# Install Python dependencies
pip install pandas numpy matplotlib ezr pathlib

# Make sure EZR is installed and in PATH
which ezr  # Should return path to EZR executable
```

---

## Usage

**Note:** We recomend enabling a virtual environment to ensure consistency!

### Basic Usage

```bash
python3 analyze_ezr_stability.py \
  --runs 50 \
  --dataset /path/to/dataset.csv \
  --stability-check 5
```

### Command-Line Arguments

```
--runs N                Number of EZR runs (default: 20)
--dataset PATH          Path to CSV dataset (required) (We recommend MOOT)
--output-dir DIR        Output directory (default: ezr_analysis)
```

---

## Output Files for each Run

### CSV Files

#### `all_trees.csv` | All generated trees with metrics:

Columns:
- `run_num`: Which run (1-N)
- `features`: Comma-separated feature names
- `complexity`: Number of features
- `win`: Accuracy percentage
- `on_frontier`: Boolean, is this tree Pareto-optimal?

#### `feature_frequency.csv` | How often each feature appears:

Columns:
- `feature`: Feature name
- `occurrences`: Count across all runs
- `frequency_%`: Percentage of all runs
- `appears_in_frontier_%`: Percentage of frontier trees

#### `pareto_front.csv` | Pareto-optimal trees

### JSON & Visualization

#### `results.json`
Complete data structure (all trees, features, stability history) in JSON format.

#### `pareto_front.png`
2D Pareto visualization (with annotations for each tree):
- **X-axis**: Complexity (# features)
- **Y-axis**: Accuracy (%)
- **Points**: Individual trees
- **Frontier**: Highlighted in color
- **Zones**: Safe (simple), Risky (complex)

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
Our general idea!

How stakeholders might pick a frontier tree based on their priority:
- Want simple? Pick the tree with fewest features on frontier
- Want accurate? Pick the tree with highest win score on frontier
- Want balanced? Pick the middle tree on frontier

---

