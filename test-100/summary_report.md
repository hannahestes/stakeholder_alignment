# SE4AI EZR Stability Analysis Report

**Generated:** 2026-04-02 10:38:54  
**Dataset:** /Users/hmestes/gits/moot/optimize/financial_data/BankChurners.csv  
**Total Runs:** 100

---

## Executive Summary

After 100 EZR runs, the optimization landscape shows:

- **Pareto Front Size:** 3 models
- **Consensus Features:** 1 (appearing in ≥80% of runs)
- **Exploratory Features:** 14 (appearing in <40% of runs)
- **Accuracy Range:** -9 to 94
- **Complexity Range:** 1 to 7 features

---

## Consensus Features (≥80% of runs)

Features that appear reliably across the optimization landscape:

- **income_Category**: 85.0% (85/100 runs)

---

## Important Features (60-80% of runs)

Features that appear frequently but not consistently:

- **education_Level**: 74.0% (74/100 runs)

---

## Exploratory Features (<40% of runs)

Features that appear rarely and may be dataset-specific artifacts:

- **CLIENTNUM**: 10.0% (10/100 runs)
- **Contacts_Count_12_mon**: 1.0% (1/100 runs)
- **Customer_Age**: 6.0% (6/100 runs)
- **Dependent_count**: 6.0% (6/100 runs)
- **Months_Inactive_12_mon**: 2.0% (2/100 runs)
- **Months_on_book**: 2.0% (2/100 runs)
- **Naive_Bayes_Classifier_Attrition_Flag_Card_Category_Contacts_Count_12_mon_Dependent_count_Education_Level_Months_Inactive_12_mon_1**: 7.0% (7/100 runs)
- **Naive_Bayes_Classifier_Attrition_Flag_Card_Category_Contacts_Count_12_mon_Dependent_count_Education_Level_Months_Inactive_12_mon_2**: 9.0% (9/100 runs)
- **Total_Amt_Chng_Q4_Q1**: 12.0% (12/100 runs)
- **Total_Relationship_Count**: 5.0% (5/100 runs)
- **Total_Trans_Amt**: 11.0% (11/100 runs)
- **Total_Trans_Ct**: 8.0% (8/100 runs)
- **attrition_Flag**: 23.0% (23/100 runs)
- **gender**: 7.0% (7/100 runs)

---

## Pareto Front Analysis

### Frontier Trees (Not dominated on both accuracy AND complexity)

1. **Run 32**: 5 features, 94 accuracy
   - Features: education_Level, marital_Status, income_Category, card_Category, Avg_Utilization_Ratio

2. **Run 18**: 4 features, 81 accuracy
   - Features: education_Level, marital_Status, income_Category, Avg_Utilization_Ratio

3. **Run 75**: 1 features, 70 accuracy
   - Features: income_Category


### Interpretation


The **knee of the curve** (best trade-off) is at Tree 75:
- Features: income_Category
- Accuracy: 70
- Complexity: 1

Trees with more features show **diminishing returns** on accuracy.

---

## Stability Analysis

Based on stability checks every 5 runs:

**Run 5:**
- Pareto front size: 2
- Consensus features: 2
- Exploratory features: 4

**Run 10:**
- Pareto front size: 2
- Consensus features: 2
- Exploratory features: 9

**Run 15:**
- Pareto front size: 4
- Consensus features: 2
- Exploratory features: 12

**Run 20:**
- Pareto front size: 3
- Consensus features: 2
- Exploratory features: 13

**Run 25:**
- Pareto front size: 3
- Consensus features: 2
- Exploratory features: 14

**Run 30:**
- Pareto front size: 3
- Consensus features: 2
- Exploratory features: 14

**Run 35:**
- Pareto front size: 4
- Consensus features: 2
- Exploratory features: 14

**Run 40:**
- Pareto front size: 4
- Consensus features: 1
- Exploratory features: 13

**Run 45:**
- Pareto front size: 4
- Consensus features: 1
- Exploratory features: 13

**Run 50:**
- Pareto front size: 4
- Consensus features: 1
- Exploratory features: 14

**Run 55:**
- Pareto front size: 4
- Consensus features: 1
- Exploratory features: 14

**Run 60:**
- Pareto front size: 4
- Consensus features: 1
- Exploratory features: 14

**Run 65:**
- Pareto front size: 4
- Consensus features: 2
- Exploratory features: 15

**Run 70:**
- Pareto front size: 5
- Consensus features: 1
- Exploratory features: 15

**Run 75:**
- Pareto front size: 3
- Consensus features: 1
- Exploratory features: 15

**Run 80:**
- Pareto front size: 3
- Consensus features: 1
- Exploratory features: 15

**Run 85:**
- Pareto front size: 3
- Consensus features: 1
- Exploratory features: 14

**Run 90:**
- Pareto front size: 3
- Consensus features: 1
- Exploratory features: 15

**Run 95:**
- Pareto front size: 3
- Consensus features: 1
- Exploratory features: 14

**Run 100:**
- Pareto front size: 3
- Consensus features: 1
- Exploratory features: 14


### Convergence Assessment

✅ **Pareto front has stabilized** (size unchanged in last check)
✅ **Consensus features have stabilized**


---

## Recommendations

1. **Feature Selection**: Use consensus features (≥80%) for production models
2. **Model Complexity**: Optimal models use 1-5 features
3. **Data Requirements**: Focus data quality efforts on consensus features
4. **Further Analysis**: Pareto front is stable; analysis is complete

---

## Data Files

- `all_trees.csv`: Complete list of all 100 generated trees
- `feature_frequency.csv`: Feature frequency analysis with classifications
- `pareto_front.csv`: Trees on the Pareto frontier
- `stability_analysis.csv`: Stability metrics by run batch
- `results.json`: All data in JSON format for programmatic access

