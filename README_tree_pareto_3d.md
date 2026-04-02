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
```json
{
  "metadata": {
    "total_trees": 50,
    "dataset": "/path/to/dataset.csv"
  },
  "trees": [
    {
      "run": 1,
      "accuracy": 75,
      "num_features": 2,
      "features": ["income_Category", "education_Level"],
      "stability": 79.0,
      "raw_output": "full EZR tree structure..."
    },
    ...
  ]
}
```

#### `frontier_trees.json`
Just the Pareto-optimal trees:
```json
{
  "metadata": {
    "frontier_size": 5,
    "accuracy_range": "64%-76%",
    "stability_range": "0%-72%"
  },
  "frontier_trees": [
    {
      "rank": 1,
      "run": 24,
      "accuracy": 76,
      "num_features": 5,
      "features": [...],
      "stability": 52.0,
      "raw_output": "..."
    },
    ...
  ]
}
```

### Visualization

#### `pareto_3d.png`
Publication-quality 3D scatter plot showing:
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

For each tree:
```
stability = average frequency of its features

Example:
Tree uses [income (80%), education (78%), marital (48%)]
stability = (80 + 78 + 48) / 3 = 68.67%
```

This metric rewards trees using frequently-selected (reliable) features.

---

## Interpreting Results

### Scenario 1: Conservative Deployment
**Choose**: Highest stability frontier tree
- **What you get**: Most generalization, minimal overfitting risk
- **What you trade**: Some accuracy
- **Best for**: Production systems, regulatory compliance

Example:
```
Run 2: 64% accuracy, 3 features, 72% stability ← Most reliable
```

### Scenario 2: Maximum Accuracy
**Choose**: Highest accuracy frontier tree
- **What you get**: Best prediction on this dataset
- **What you trade**: Lower stability (may not generalize)
- **Best for**: Research, exploratory analysis

Example:
```
Run 24: 76% accuracy, 5 features, 52% stability ← Best prediction
```

### Scenario 3: Balanced Production
**Choose**: Middle of frontier
- **What you get**: Good accuracy + reasonable stability
- **What you trade**: Neither optimized
- **Best for**: Cross-functional teams, sustainable deployment

Example:
```
Run 43: 74% accuracy, 4 features, 60% stability ← Sweet spot
```

### Scenario 4: Maximum Simplicity
**Choose**: Fewest features with acceptable accuracy
- **What you get**: Easy to implement, explain, maintain
- **What you trade**: Some accuracy
- **Best for**: Real-time systems, mobile deployment

Example:
```
Run 5: 71% accuracy, 2 features, 71% stability ← Simplicity champion
```

---

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

---

## Customization

### Changing Number of Runs

```bash
python3 tree_pareto_3d.py \
  --runs 100 \  # More runs = more thorough analysis
  --dataset ~/path/to/data.csv
```

More runs = better frontier approximation, longer runtime.

### Changing Output Directory

```bash
python3 tree_pareto_3d.py \
  --runs 50 \
  --dataset ~/path/to/data.csv \
  --output-dir my_results/
```

### Modifying Code

Edit `tree_pareto_3d.py` to customize:
- **Pareto dominance logic** (line ~195): Change how frontier is calculated
- **Knee point algorithm** (line ~225): Change optimization criteria
- **Visualization** (line ~270): Adjust colors, angles, labels
- **Feature extraction** (line ~60): Modify how features are parsed from EZR output

---

## Workflow Example

### 1. Prepare Dataset
```bash
# Ensure dataset is in CSV format
head my_dataset.csv
```

### 2. Run Analysis
```bash
python3 tree_pareto_3d.py \
  --runs 50 \
  --dataset my_dataset.csv
```

### 3. Review Outputs
```bash
ls -la tree_analysis_3d/

# CSVs: inspect frontier, features
head tree_analysis_3d/pareto_frontier_3d.csv

# JSON: detailed tree structures
cat tree_analysis_3d/frontier_trees.json | python -m json.tool

# PNG: visualize trade-offs
open tree_analysis_3d/pareto_3d.png
```

### 4. Select a Solution
- Read the frontier CSV and PNG
- Check stakeholder priorities (accuracy? simplicity? stability?)
- Choose a frontier tree from `pareto_frontier_3d.csv`
- Find the full tree structure in `frontier_trees.json`

### 5. Validate & Deploy
```bash
# Use the selected tree's raw_output (EZR format)
# to implement rules in your system
```

---

## Example: Step-by-Step

```bash
# 1. Run analysis
python3 tree_pareto_3d.py --runs 50 --dataset BankChurners.csv

# 2. Check frontier
cat tree_analysis_3d/pareto_frontier_3d.csv
# Output:
# run,accuracy,features,num_features,feature_set,stability
# 24,76,"['card_Category', 'education_Level', 'income_Category', 'marital_Status', 'Naive_Bayes_Classifier...']",5,...,52.0
# 43,74,"['Avg_Utilization_Ratio', 'card_Category', 'education_Level', 'income_Category']",4,...,60.0
# 5,71,"['income_Category', 'marital_Status']",2,...,71.0
# 2,64,"['education_Level', 'income_Category', 'marital_Status']",3,...,72.0
# 8,64,"[]",0,...,0.0

# 3. View visualization
open tree_analysis_3d/pareto_3d.png
# Shows 5 frontier trees, 45 off-frontier trees, zones

# 4. Get top features
cat tree_analysis_3d/feature_frequency_summary.csv
# Shows income_Category: 80%, education_Level: 78%, etc.

# 5. Inspect best tree (Run 5: 71% accuracy, 2 features)
cat tree_analysis_3d/frontier_trees.json | grep -A 20 '"rank": 3'
# Get full tree structure for implementation

# 6. Decide
# If you want simplicity: Use Run 5 (2 features, 71% accuracy, 71% stable)
# If you want accuracy: Use Run 24 (5 features, 76% accuracy, 52% stable)
# If you want balance: Use Run 43 (4 features, 74% accuracy, 60% stable)
```

---

## Troubleshooting

### Error: `ezr: command not found`
**Solution**: Ensure EZR is installed and in your PATH.
```bash
which ezr  # Check if installed
echo $PATH  # Verify EZR directory is in PATH
```

### Error: `FileNotFoundError: dataset.csv`
**Solution**: Use absolute path or ensure file exists.
```bash
python3 tree_pareto_3d.py \
  --runs 50 \
  --dataset ~/gits/moot/optimize/financial_data/BankChurners.csv
```

### Error: `AttributeError: 'Tree3DAnalyzer' object has no attribute 'save_outputs'`
**Solution**: Ensure you're using the latest version of the script.
```bash
git pull origin main  # Or re-download the script
```

### No frontier trees (empty pareto_frontier_3d.csv)
**Cause**: EZR found very few valid trees or all trees dominate each other poorly.
**Solution**: Increase runs (`--runs 100`) or check dataset quality.

---

## Performance Notes

- **Runtime**: ~30 seconds per run (depends on dataset size)
  - 50 runs: ~25-30 minutes
  - 100 runs: ~50-60 minutes
- **Memory**: Minimal (all data fits in RAM for typical datasets)
- **Disk**: ~5-10 MB output (mostly JSON with raw EZR output)

---

## Citation & References

This tool implements:
- **3D Pareto optimization** for decision trees
- **Feature frequency stability** metric (not exact feature-set matching)
- **Knee point detection** using normalized composite scores
- **Convergent Divergence** framework for multi-objective decision-making

Reference paper model: ACM DOI 10.1145/3796511

---

## FAQ

**Q: Why does EZR give different results each run?**  
A: Tree induction is stochastic. This variation shows which solutions are robust (appear in frontier consistently) vs. random.

**Q: Can I use just the highest-accuracy tree?**  
A: Yes, if accuracy is your only priority. But check stability — high accuracy + low stability = may not generalize.

**Q: What's "feature frequency stability"?**  
A: For each tree, it's the average frequency of its features across all 50 runs. Trees using frequently-selected features are more "stable."

**Q: Why 5 dimensions (3D + Pareto frontier size)?**  
A: The frontier itself is 1D (a set of trees). We visualize 3 objectives in 3D space. The frontier is the set of non-dominated solutions.

**Q: How do I deploy a chosen tree?**  
A: Extract the `raw_output` field from `frontier_trees.json`. It contains the full EZR tree structure (if/then rules) ready to implement.

---

## Support

For issues or questions:
1. Check the **Troubleshooting** section above
2. Review the **output files** to verify EZR is working correctly
3. Inspect `raw_output` in JSON files to see actual trees
4. Increase `--runs` to improve frontier approximation

---

## License

Same as the parent project.

---

*Generated by: tree_pareto_3d.py | Last updated: April 2025*
