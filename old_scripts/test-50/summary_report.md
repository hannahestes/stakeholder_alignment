# SE4AI EZR Stability Analysis Report

**Generated:** 2026-04-01 13:55:15  
**Dataset:** /Users/hmestes/gits/moot/optimize/financial_data/BankChurners.csv  
**Total Runs:** 50

---

## Executive Summary

After 50 EZR runs, the optimization landscape shows:

- **Pareto Front Size:** 4 models
- **Consensus Features:** 0 (appearing in ≥80% of runs)
- **Exploratory Features:** 15 (appearing in <40% of runs)
- **Accuracy Range:** -66 to -3
- **Complexity Range:** 2 to 7 features

---

## Consensus Features (≥80% of runs)

Features that appear reliably across the optimization landscape:

No consensus features at ≥80% threshold.

---

## Important Features (60-80% of runs)

Features that appear frequently but not consistently:

- **income_Category**: 78.0% (39/50 runs)
- **education_Level**: 72.0% (36/50 runs)

---

## Exploratory Features (<40% of runs)

Features that appear rarely and may be dataset-specific artifacts:

- **CLIENTNUM**: 12.0% (6/50 runs)
- **Contacts_Count_12_mon**: 2.0% (1/50 runs)
- **Customer_Age**: 4.0% (2/50 runs)
- **Dependent_count**: 2.0% (1/50 runs)
- **Months_on_book**: 4.0% (2/50 runs)
- **Naive_Bayes_Classifier_Attrition_Flag_Card_Category_Contacts_Count_12_mon_Dependent_count_Education_Level_Months_Inactive_12_mon_1**: 4.0% (2/50 runs)
- **Naive_Bayes_Classifier_Attrition_Flag_Card_Category_Contacts_Count_12_mon_Dependent_count_Education_Level_Months_Inactive_12_mon_2**: 6.0% (3/50 runs)
- **Total_Amt_Chng_Q4_Q1**: 12.0% (6/50 runs)
- **Total_Relationship_Count**: 2.0% (1/50 runs)
- **Total_Trans_Amt**: 24.0% (12/50 runs)
- **Total_Trans_Ct**: 12.0% (6/50 runs)
- **attrition_Flag**: 26.0% (13/50 runs)
- **card_Category**: 38.0% (19/50 runs)
- **gender**: 16.0% (8/50 runs)
- **marital_Status**: 38.0% (19/50 runs)

---

## Pareto Front Analysis

### Frontier Trees (Not dominated on both accuracy AND complexity)

1. **Run 35**: 7 features, -3 accuracy
   - Features: CLIENTNUM, attrition_Flag, gender, education_Level, marital_Status, income_Category, card_Category

2. **Run 41**: 4 features, -9 accuracy
   - Features: education_Level, income_Category, Total_Trans_Amt, Avg_Utilization_Ratio

3. **Run 50**: 3 features, -15 accuracy
   - Features: gender, income_Category, Total_Trans_Amt

4. **Run 9**: 2 features, -21 accuracy
   - Features: education_Level, Avg_Utilization_Ratio


### Interpretation


The **knee of the curve** (best trade-off) is at Tree 9:
- Features: education_Level, Avg_Utilization_Ratio
- Accuracy: -21
- Complexity: 2

Trees with more features show **diminishing returns** on accuracy.

---

## Stability Analysis

Based on stability checks every 5 runs:

**Run 5:**
- Pareto front size: 2
- Consensus features: 2
- Exploratory features: 3

**Run 10:**
- Pareto front size: 1
- Consensus features: 1
- Exploratory features: 9

**Run 15:**
- Pareto front size: 1
- Consensus features: 1
- Exploratory features: 9

**Run 20:**
- Pareto front size: 1
- Consensus features: 0
- Exploratory features: 9

**Run 25:**
- Pareto front size: 1
- Consensus features: 0
- Exploratory features: 10

**Run 30:**
- Pareto front size: 1
- Consensus features: 0
- Exploratory features: 11

**Run 35:**
- Pareto front size: 4
- Consensus features: 0
- Exploratory features: 12

**Run 40:**
- Pareto front size: 4
- Consensus features: 0
- Exploratory features: 13

**Run 45:**
- Pareto front size: 4
- Consensus features: 0
- Exploratory features: 14

**Run 50:**
- Pareto front size: 4
- Consensus features: 0
- Exploratory features: 15


### Convergence Assessment

✅ **Pareto front has stabilized** (size unchanged in last check)
✅ **Consensus features have stabilized**


---

## Recommendations

1. **Feature Selection**: Use consensus features (≥80%) for production models
2. **Model Complexity**: Optimal models use 2-7 features
3. **Data Requirements**: Focus data quality efforts on consensus features
4. **Further Analysis**: Pareto front is stable; analysis is complete

---

## Data Files

- `all_trees.csv`: Complete list of all 50 generated trees
- `feature_frequency.csv`: Feature frequency analysis with classifications
- `pareto_front.csv`: Trees on the Pareto frontier
- `stability_analysis.csv`: Stability metrics by run batch
- `results.json`: All data in JSON format for programmatic access

