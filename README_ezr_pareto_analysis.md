# EZR Pareto Analysis

`ezr_pareto_analysis.py` runs EZR N times and produces both **2D** and **3D** Pareto frontier analyses in one command. EZR is run once — results are shared across both analyses.

---

## The Three Dimensions

| Dimension | Meaning |
|---|---|
| **Accuracy** | EZR's final win% for the tree |
| **Complexity** | Number of features used (same axis in 2D and 3D) |
| **Stability** | Average frequency of the tree's features across all runs (3D only) |

The 3D analysis is the 2D analysis with stability added as a third dimension.

---

## Usage

```bash
python3 ezr_pareto_analysis.py --runs 50 --dataset ~/gits/moot/optimize/financial_data/BankChurners.csv --output-dir testing/
```

| Argument | Default | Description |
|---|---|---|
| `--dataset PATH` | *(required)* | Path to dataset CSV |
| `--runs N` | `50` | Number of EZR runs |
| `--output-dir DIR` | `ezr_output` | Output directory |

---

## Outputs

```
ezr_output/
  all_trees.csv          Every run: accuracy, complexity, stability, frontier membership
  feature_frequency.csv  How often each feature appeared across all runs
  all_trees.json         Full tree data for every run, including raw decision tree output
  pareto_2d.json         2D frontier trees with rank, metrics, and raw output
  pareto_3d.json         3D frontier trees with rank, metrics, and raw output
  pareto_2d.png          Accuracy vs. Complexity scatter — all runs labeled, frontier highlighted
  pareto_3d.png          Accuracy × Complexity × Stability 3D scatter with % axis labels
```

---

## Understanding the Frontiers

**2D** — A tree is on the frontier if no other tree has both higher accuracy and lower complexity. The **knee** is the simplest tree that doesn't sacrifice accuracy.

**3D** — A tree is on the frontier if no other tree is strictly better on all three dimensions. The **knee** (red star) is the tree with the best normalized balance across all three.

### Choosing a frontier tree

- **Want simple?** Pick the frontier tree with the fewest features
- **Want accurate?** Pick the frontier tree with the highest win score
- **Want stable?** Pick the frontier tree with the highest stability %
- **Want balanced?** Use the **knee point** (red star) — it optimizes all three

This supports *Convergent Divergence*: teams converge on the fact that multiple valid solutions exist, then diverge on which trade-off fits their context.

### Stability thresholds

| Range | Reliability |
|---|---|
| 70%+ | Very reliable — uses core features |
| 50–70% | Reasonable — mixed reliability |
| <50% | Risky — uses exploratory features |

---

## Dependencies

```bash
pip install pandas numpy matplotlib
```

EZR must be installed and available as `ezr` in PATH.
