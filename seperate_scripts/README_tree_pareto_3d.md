# 3D Pareto Front Analysis: tree_pareto_3d.py

## Overview

`tree_pareto_3d.py` runs **Explainable Rule Extraction (EZR)** multiple times on a dataset and analyzes the resulting decision trees using **3D Pareto frontier analysis**. It discovers trade-offs between three objectives:

- **Accuracy (Z-axis)**: How well does the tree predict?
- **Simplicity (X-axis)**: How many features does it use?
- **Stability (Y-axis)**: How reliable are its features across runs?

This tool supports **"Convergent Divergence"** — helping teams converge on the fact that multiple valid solutions exist, while diverging on how to prioritize accuracy vs. simplicity vs. generalization.

---

## What It Does

1. **Runs EZR N times** (typically 50 runs)
2. **Extracts metrics** from each tree:
   - Accuracy (%)
   - Features used
   - Feature frequency stability
3. **Calculates 3D Pareto frontier** (non-dominated solutions)
4. **Identifies the knee point** (optimal balance)
5. **Generates outputs**:
   - CSV files (trees, frontier, feature frequency)
   - JSON files (full tree structures + raw EZR output)
   - 3D visualization (publication-quality PNG)
   - Summary statistics

---

## Dependencies

- **Python 3.7+**
- **EZR** (Explainable Rule Extraction) — must be installed and available as `ezr` command
- **pandas** — data manipulation
- **numpy** — numerical operations
- **matplotlib** — 3D visualization
- **pathlib** — file path handling

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
python3 tree_pareto_3d.py \
  --runs 50 \
  --dataset /path/to/dataset.csv
```

### Command-Line Arguments

```
--runs N              Number of EZR runs (default: 50)
--dataset PATH        Path to CSV dataset (required)
--output-dir DIR      Output directory (default: tree_analysis_3d)
```

### Example

```bash
python3 tree_pareto_3d.py \
  --runs 50 \
  --dataset ~/gits/moot/optimize/financial_data/BankChurners.csv
```

---

## Output Files

### CSV Files

#### `trees_analyzed.csv`
All 50 trees with metrics:
```
run,accuracy,features,num_features,feature_set,stability,feature_set_name,raw_output
1,75,"['income_Category', 'education_Level']",2,...
2,68,"['income_Category', 'marital_Status']",2,...
```

#### `pareto_frontier_3d.csv`
Pareto-optimal trees only (typically 5-8 trees):
```
run,accuracy,features,num_features,feature_set,stability,feature_set_name
24,76,"['card_Category', 'education_Level', ...]",5,...
5,71,"['income_Category', 'marital_Status']",2,...
```

#### `feature_frequency_summary.csv`
How often each feature appears across 50 runs:
```
feature,occurrences,frequency_%
income_Category,40,80.0
education_Level,39,78.0
card_Category,19,38.0
```

### JSON Files

#### `all_trees.json`
Complete tree structures for all 50 runs:


### Visualization

#### `pareto_3d.png`
- **Off-frontier trees**: Grey circles (subtle)
- **Frontier trees**: Colored circles (red = high accuracy, yellow = medium, green = low)
- **Knee point**: Red star (optimal balance)
- **Surface**: Triangulated mesh of frontier
- **Zones**: Safe (simple+stable), Risky (complex+unstable)
- **Legend**: Color scheme and symbol key

---

## Understanding the Output

### 3D Space

```
Z (Vertical): ACCURACY (%)
              How well does the tree predict?

Y (Back-Left): STABILITY (% Feature Frequency)
               How often do its features appear across runs?

X (Front-Right): SIMPLICITY (# Features)
                 How many features does it use?
```

### Pareto Frontier

A tree is on the **frontier** if no other tree is strictly better in all three dimensions:
- Higher accuracy
- Fewer features (simpler)
- Higher stability (more reliable)

### Feature Frequency Stability

This metric rewards trees using frequently-selected (reliable) features.

stability = average frequency of its features

## Key Metrics

### Accuracy
EZR's final win% on the dataset. Higher is better, but may not generalize.

### Simplicity (# Features)
Fewer features = easier to interpret, implement, and maintain.
Trade-off: May sacrifice predictive power.

### Stability (Feature Frequency %)
Percentage reflecting how often the tree's features appear across runs.
- **70%+**: Very reliable, uses core features
- **50-70%**: Reasonable, mixed reliability
- **<50%**: Risky, uses exploratory features
