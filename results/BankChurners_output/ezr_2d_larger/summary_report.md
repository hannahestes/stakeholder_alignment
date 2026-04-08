# SE4AI EZR Stability Analysis Report

**Generated:** 2026-04-02 10:00:08  
**Dataset:** /Users/hmestes/gits/moot/optimize/financial_data/BankChurners.csv  
**Total Runs:** 50

---

## Executive Summary

After 50 EZR runs, the optimization landscape shows:

- **Pareto Front Size:** 4 models
- **Consensus Features:** 1 (appearing in ≥80% of runs)
- **Exploratory Features:** 15 (appearing in <40% of runs)
- **Accuracy Range:** 0 to 100
- **Complexity Range:** 2 to 6 features

---

## Consensus Features (≥80% of runs)

Features that appear reliably across the optimization landscape:

- **income_Category**: 96.0% (48/50 runs)

---

## Important Features (60-80% of runs)

Features that appear frequently but not consistently:

- **education_Level**: 62.0% (31/50 runs)

---

## Exploratory Features (<40% of runs)

Features that appear rarely and may be dataset-specific artifacts:

- **CLIENTNUM**: 4.0% (2/50 runs)
- **Contacts_Count_12_mon**: 4.0% (2/50 runs)
- **Customer_Age**: 4.0% (2/50 runs)
- **Dependent_count**: 4.0% (2/50 runs)
- **Months_Inactive_12_mon**: 2.0% (1/50 runs)
- **Months_on_book**: 2.0% (1/50 runs)
- **Naive_Bayes_Classifier_Attrition_Flag_Card_Category_Contacts_Count_12_mon_Dependent_count_Education_Level_Months_Inactive_12_mon_1**: 8.0% (4/50 runs)
- **Naive_Bayes_Classifier_Attrition_Flag_Card_Category_Contacts_Count_12_mon_Dependent_count_Education_Level_Months_Inactive_12_mon_2**: 4.0% (2/50 runs)
- **Total_Amt_Chng_Q4_Q1**: 4.0% (2/50 runs)
- **Total_Relationship_Count**: 4.0% (2/50 runs)
- **Total_Trans_Amt**: 10.0% (5/50 runs)
- **Total_Trans_Ct**: 4.0% (2/50 runs)
- **attrition_Flag**: 22.0% (11/50 runs)
- **gender**: 14.0% (7/50 runs)
- **marital_Status**: 36.0% (18/50 runs)

---

## Pareto Front Analysis

### Frontier Trees (Not dominated on both accuracy AND complexity)

1. **Run 26**: 6 features, 100 accuracy
   - Features: education_Level, income_Category, Total_Amt_Chng_Q4_Q1, Total_Trans_Amt, Total_Trans_Ct, Avg_Utilization_Ratio

2. **Run 44**: 4 features, 98 accuracy
   - Features: education_Level, income_Category, card_Category, Avg_Utilization_Ratio

3. **Run 22**: 3 features, 77 accuracy
   - Features: education_Level, marital_Status, Avg_Utilization_Ratio

4. **Run 24**: 2 features, 68 accuracy
   - Features: income_Category, Avg_Utilization_Ratio


### Interpretation


The **knee of the curve** (best trade-off) is at Tree 24:
- Features: income_Category, Avg_Utilization_Ratio
- Accuracy: 68
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
- Pareto front size: 2
- Consensus features: 1
- Exploratory features: 4

**Run 15:**
- Pareto front size: 2
- Consensus features: 1
- Exploratory features: 8

**Run 20:**
- Pareto front size: 2
- Consensus features: 1
- Exploratory features: 10

**Run 25:**
- Pareto front size: 2
- Consensus features: 1
- Exploratory features: 10

**Run 30:**
- Pareto front size: 3
- Consensus features: 1
- Exploratory features: 13

**Run 35:**
- Pareto front size: 4
- Consensus features: 1
- Exploratory features: 12

**Run 40:**
- Pareto front size: 4
- Consensus features: 1
- Exploratory features: 13

**Run 45:**
- Pareto front size: 4
- Consensus features: 1
- Exploratory features: 14

**Run 50:**
- Pareto front size: 4
- Consensus features: 1
- Exploratory features: 15


### Convergence Assessment

✅ **Pareto front has stabilized** (size unchanged in last check)
✅ **Consensus features have stabilized**


---

## Recommendations

1. **Feature Selection**: Use consensus features (≥80%) for production models
2. **Model Complexity**: Optimal models use 2-6 features
3. **Data Requirements**: Focus data quality efforts on consensus features
4. **Further Analysis**: Pareto front is stable; analysis is complete

---

## Data Files

- `all_trees.csv`: Complete list of all 50 generated trees
- `feature_frequency.csv`: Feature frequency analysis with classifications
- `pareto_front.csv`: Trees on the Pareto frontier
- `stability_analysis.csv`: Stability metrics by run batch
- `results.json`: All data in JSON format for programmatic access

