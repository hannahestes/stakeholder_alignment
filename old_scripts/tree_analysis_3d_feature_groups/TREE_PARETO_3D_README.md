# 3D Pareto Analysis: Trees on Accuracy × Simplicity × Stability

## Overview

This analysis evaluates **all 50 EZR decision trees** on a **3D Pareto frontier** measuring three critical trade-offs:

```
ACCURACY (Z-axis)
  ↑
  |           (high accuracy, complex, stable)
  |         /
  |        /
  +-------→ SIMPLICITY (X-axis: # of features)
 /
/
STABILITY (Y-axis: % of runs with same feature set)
```

---

## The Three Dimensions

### **1. Accuracy**
- **Metric**: Final win% (improvement over baseline)
- **Range**: 0-100%
- **Interpretation**: Higher = better predictive performance

### **2. Simplicity**
- **Metric**: Number of unique features used in the tree
- **Range**: 1-N features
- **Interpretation**: Fewer features = easier to understand, implement, and maintain

### **3. Stability**
- **Metric**: Feature set penetration (how many of 50 runs used the same features)
- **Range**: 0-100%
- **Calculation**: If 35 out of 50 runs produce trees using [A, B, C], stability = 70%
- **Interpretation**: Higher = more robust (EZR consistently picks these features)

---

## The Pareto Frontier

A tree is on the **frontier** if no other tree dominates it on all 3 dimensions simultaneously.

**Domination rule:** Tree B dominates Tree A if:
- B has ≥ accuracy AND
- B has ≤ features AND  
- B has ≥ stability
- AND B is strictly better on at least one dimension

**Example:**
```
Tree A: 75% accuracy, 5 features, 60% stability
Tree B: 80% accuracy, 4 features, 65% stability

→ Tree B dominates Tree A (better on all three!)
→ Tree A is OFF frontier
```

---

## Output Files

### **trees_analyzed.csv**
All 50 trees with their 3D metrics:

```csv
run,accuracy,features,num_features,feature_set,stability,feature_set_name
1,"[Avg_Utilization_Ratio, Total_Trans_Ct]",2,40.0,"Avg_Utilization_Ratio, Total_Trans_Ct"
2,"[Avg_Utilization_Ratio, card_Category, income_Category]",3,22.0,"Avg_Utilization_Ratio, card_Category, income_Category"
...
```

### **pareto_frontier_3d.csv**
Only the trees on the Pareto frontier (non-dominated):

```csv
run,accuracy,num_features,stability,feature_set_name
12,85,3,45.0,"Avg_Utilization_Ratio, Total_Trans_Ct, card_Category"
7,82,2,60.0,"Avg_Utilization_Ratio, card_Category"
...
```

### **feature_sets_summary.csv**
Aggregated view of feature combinations:

```csv
features,num_features,occurrences,stability_%
"Avg_Utilization_Ratio, Total_Trans_Ct",2,30,60.0
"Avg_Utilization_Ratio, card_Category",2,25,50.0
"income_Category, education_Level",2,8,16.0
...
```

### **pareto_3d.png**
3D scatter plot showing:
- Gray dots = off-frontier trees
- Green dots = frontier trees
- Labels on each frontier tree
- Summary statistics box

---

## Interpreting the Results

### **What makes a tree "strong"?**

**High on all three dimensions** (rare):
```
- Accuracy: 85%+
- Features: 2-3
- Stability: 70%+

→ "This tree is accurate, simple, AND robust!"
```

**Pareto trade-offs** (common):
```
Tree A: 88% accuracy, 5 features, 40% stability
  → High performance but complex and flaky

Tree B: 78% accuracy, 2 features, 70% stability
  → Lower performance but simpler and more robust

→ Different stakeholders will prefer different trees
```

---

## Key Insights to Look For

### **1. Feature Consistency**
- Are the same features appearing across runs?
- **High stability** = EZR reliably picks these features
- **Low stability** = Different runs pick completely different features

### **2. Accuracy-Simplicity Trade-off**
- Can you get 80%+ accuracy with just 2-3 features?
- Or does accuracy require 6+ features?
- Affects deployability significantly

### **3. Robustness Question**
- Best accuracy (88%) but only appears in 1 run (2% stability)?
  - → May be overfitting to that particular random seed
- Medium accuracy (78%) but appears in 35 runs (70% stability)?
  - → More trustworthy for deployment

### **4. Frontier Size**
- 2-3 frontier trees = strong consensus (few good trees)
- 10+ frontier trees = weak consensus (many trade-off options)

---

## Stakeholder Use Cases

### **For Tim (Performance-focused)**
Sort by accuracy, then pick high-accuracy trees regardless of other dimensions.

### **For Abi (Simplicity-focused)**
Sort by num_features, prioritize trees with ≤3 features even if accuracy is lower.

### **For Pat (Balanced)**
Look for trees in the "sweet spot":
- 75%+ accuracy
- 2-4 features
- 50%+ stability

---

## Running the Analysis

```bash
python3 tree_pareto_3d.py \
  --runs 50 \
  --dataset ~/gits/moot/optimize/financial_data/BankChurners.csv
```

**Output:** 
```
🚀 Running EZR 50 times...
  ✓ Completed 10/50 runs
  ✓ Completed 20/50 runs
  ...
  ✓ Completed 50/50 runs

✅ Analysis complete: 50 trees analyzed

💾 Saving outputs...
  ✓ trees_analyzed.csv
  ✓ pareto_frontier_3d.csv
  ✓ feature_sets_summary.csv
  ✓ pareto_3d.png

80 PARETO ANALYSIS SUMMARY
================================================================================

Total Trees: 50
Frontier Size: 7

Accuracy Range: 65% - 88%
Simplicity Range: 1 - 8 features
Stability Range: 2% - 70%

TOP FRONTIER TREES
...
```

---

## For Your Research

This 3D analysis gives you:

1. ✅ **Richer Pareto frontier** — More trees on it, more nuance
2. ✅ **Real trade-offs** — Accuracy vs. complexity vs. robustness are genuine
3. ✅ **Authenticity** — Feature set stability is a real measure of robustness
4. ✅ **Clearer divergence** — Different personas genuinely prefer different trees

The 3D frontier reveals which trees are:
- High-performance but risky (high accuracy, low stability)
- Robust but conservative (lower accuracy, high stability)
- Balanced (medium on all three)

This is exactly the kind of divergence that fuels stakeholder discussion!
