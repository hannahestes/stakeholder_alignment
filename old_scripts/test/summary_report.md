# SE4AI EZR Stability Analysis Report

**Generated:** 2026-04-01 13:43:42  
**Dataset:** /Users/hmestes/gits/moot/optimize/financial_data/BankChurners.csv  
**Total Runs:** 20

---

## Executive Summary

After 20 EZR runs, the optimization landscape shows:

- **Pareto Front Size:** 3 models
- **Consensus Features:** 0 (appearing in ≥80% of runs)
- **Exploratory Features:** 12 (appearing in <40% of runs)
- **Accuracy Range:** -63 to -15
- **Complexity Range:** 2 to 6 features

---

## Consensus Features (≥80% of runs)

Features that appear reliably across the optimization landscape:

No consensus features at ≥80% threshold.

---

## Important Features (60-80% of runs)

Features that appear frequently but not consistently:

- **education_Level**: 75.0% (15/20 runs)
- **income_Category**: 75.0% (15/20 runs)
- **Avg_Utilization_Ratio**: 65.0% (13/20 runs)
- **marital_Status**: 60.0% (12/20 runs)

---

## Exploratory Features (<40% of runs)

Features that appear rarely and may be dataset-specific artifacts:

- **CLIENTNUM**: 15.0% (3/20 runs)
- **Customer_Age**: 15.0% (3/20 runs)
- **Months_Inactive_12_mon**: 15.0% (3/20 runs)
- **Months_on_book**: 5.0% (1/20 runs)
- **Naive_Bayes_Classifier_Attrition_Flag_Card_Category_Contacts_Count_12_mon_Dependent_count_Education_Level_Months_Inactive_12_mon_2**: 5.0% (1/20 runs)
- **Total_Amt_Chng_Q4_Q1**: 10.0% (2/20 runs)
- **Total_Relationship_Count**: 5.0% (1/20 runs)
- **Total_Trans_Amt**: 10.0% (2/20 runs)
- **Total_Trans_Ct**: 5.0% (1/20 runs)
- **attrition_Flag**: 20.0% (4/20 runs)
- **card_Category**: 15.0% (3/20 runs)
- **gender**: 5.0% (1/20 runs)

---

## Pareto Front Analysis

### Frontier Trees (Not dominated on both accuracy AND complexity)

1. **Run 10**: 5 features, -15 accuracy
   - Features: attrition_Flag, education_Level, marital_Status, income_Category, card_Category

2. **Run 14**: 4 features, -18 accuracy
   - Features: education_Level, marital_Status, income_Category, Avg_Utilization_Ratio

3. **Run 12**: 2 features, -20 accuracy
   - Features: education_Level, Total_Trans_Amt


### Interpretation


The **knee of the curve** (best trade-off) is at Tree 12:
- Features: education_Level, Total_Trans_Amt
- Accuracy: -20
- Complexity: 2

Trees with more features show **diminishing returns** on accuracy.

---

## Stability Analysis

Based on stability checks every 5 runs:

**Run 5:**
- Pareto front size: 2
- Consensus features: 1
- Exploratory features: 3

**Run 10:**
- Pareto front size: 3
- Consensus features: 1
- Exploratory features: 8

**Run 15:**
- Pareto front size: 3
- Consensus features: 0
- Exploratory features: 10

**Run 20:**
- Pareto front size: 3
- Consensus features: 0
- Exploratory features: 12


### Convergence Assessment

✅ **Pareto front has stabilized** (size unchanged in last check)
✅ **Consensus features have stabilized**


---

## Recommendations

1. **Feature Selection**: Use consensus features (≥80%) for production models
2. **Model Complexity**: Optimal models use 2-5 features
3. **Data Requirements**: Focus data quality efforts on consensus features
4. **Further Analysis**: Pareto front is stable; analysis is complete

---

## Data Files

- `all_trees.csv`: Complete list of all 20 generated trees
- `feature_frequency.csv`: Feature frequency analysis with classifications
- `pareto_front.csv`: Trees on the Pareto frontier
- `stability_analysis.csv`: Stability metrics by run batch
- `results.json`: All data in JSON format for programmatic access

