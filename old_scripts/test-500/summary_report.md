# SE4AI EZR Stability Analysis Report

**Generated:** 2026-04-01 14:01:03  
**Dataset:** /Users/hmestes/gits/moot/optimize/financial_data/BankChurners.csv  
**Total Runs:** 500

---

## Executive Summary

After 500 EZR runs, the optimization landscape shows:

- **Pareto Front Size:** 3 models
- **Consensus Features:** 1 (appearing in ≥80% of runs)
- **Exploratory Features:** 16 (appearing in <40% of runs)
- **Accuracy Range:** -112 to 0
- **Complexity Range:** 1 to 8 features

---

## Consensus Features (≥80% of runs)

Features that appear reliably across the optimization landscape:

- **income_Category**: 84.4% (421/500 runs)

---

## Important Features (60-80% of runs)

Features that appear frequently but not consistently:

- **education_Level**: 67.4% (337/500 runs)

---

## Exploratory Features (<40% of runs)

Features that appear rarely and may be dataset-specific artifacts:

- **CLIENTNUM**: 9.4% (47/500 runs)
- **Contacts_Count_12_mon**: 3.4% (17/500 runs)
- **Customer_Age**: 8.4% (42/500 runs)
- **Dependent_count**: 5.8% (29/500 runs)
- **Months_Inactive_12_mon**: 1.6% (8/500 runs)
- **Months_on_book**: 7.2% (36/500 runs)
- **Naive_Bayes_Classifier_Attrition_Flag_Card_Category_Contacts_Count_12_mon_Dependent_count_Education_Level_Months_Inactive_12_mon_1**: 7.2% (36/500 runs)
- **Naive_Bayes_Classifier_Attrition_Flag_Card_Category_Contacts_Count_12_mon_Dependent_count_Education_Level_Months_Inactive_12_mon_2**: 6.0% (30/500 runs)
- **Total_Amt_Chng_Q4_Q1**: 13.0% (65/500 runs)
- **Total_Relationship_Count**: 6.8% (34/500 runs)
- **Total_Trans_Amt**: 13.6% (68/500 runs)
- **Total_Trans_Ct**: 7.8% (39/500 runs)
- **attrition_Flag**: 17.6% (88/500 runs)
- **card_Category**: 36.0% (180/500 runs)
- **gender**: 11.6% (58/500 runs)
- **marital_Status**: 39.4% (196/500 runs)

---

## Pareto Front Analysis

### Frontier Trees (Not dominated on both accuracy AND complexity)

1. **Run 446**: 5 features, 0 accuracy
   - Features: attrition_Flag, gender, education_Level, marital_Status, income_Category

2. **Run 108**: 2 features, -2 accuracy
   - Features: education_Level, income_Category

3. **Run 417**: 1 features, -19 accuracy
   - Features: income_Category


### Interpretation


The **knee of the curve** (best trade-off) is at Tree 417:
- Features: income_Category
- Accuracy: -19
- Complexity: 1

Trees with more features show **diminishing returns** on accuracy.

---

## Stability Analysis

Based on stability checks every 5 runs:

**Run 5:**
- Pareto front size: 2
- Consensus features: 2
- Exploratory features: 5

**Run 10:**
- Pareto front size: 2
- Consensus features: 2
- Exploratory features: 10

**Run 15:**
- Pareto front size: 2
- Consensus features: 2
- Exploratory features: 13

**Run 20:**
- Pareto front size: 2
- Consensus features: 1
- Exploratory features: 14

**Run 25:**
- Pareto front size: 3
- Consensus features: 1
- Exploratory features: 16

**Run 30:**
- Pareto front size: 2
- Consensus features: 1
- Exploratory features: 16

**Run 35:**
- Pareto front size: 2
- Consensus features: 1
- Exploratory features: 16

**Run 40:**
- Pareto front size: 2
- Consensus features: 1
- Exploratory features: 16

**Run 45:**
- Pareto front size: 2
- Consensus features: 1
- Exploratory features: 16

**Run 50:**
- Pareto front size: 2
- Consensus features: 1
- Exploratory features: 16

**Run 55:**
- Pareto front size: 2
- Consensus features: 1
- Exploratory features: 16

**Run 60:**
- Pareto front size: 2
- Consensus features: 1
- Exploratory features: 16

**Run 65:**
- Pareto front size: 2
- Consensus features: 1
- Exploratory features: 16

**Run 70:**
- Pareto front size: 2
- Consensus features: 1
- Exploratory features: 16

**Run 75:**
- Pareto front size: 2
- Consensus features: 1
- Exploratory features: 15

**Run 80:**
- Pareto front size: 2
- Consensus features: 1
- Exploratory features: 15

**Run 85:**
- Pareto front size: 2
- Consensus features: 1
- Exploratory features: 15

**Run 90:**
- Pareto front size: 2
- Consensus features: 1
- Exploratory features: 15

**Run 95:**
- Pareto front size: 2
- Consensus features: 1
- Exploratory features: 15

**Run 100:**
- Pareto front size: 2
- Consensus features: 1
- Exploratory features: 15

**Run 105:**
- Pareto front size: 2
- Consensus features: 1
- Exploratory features: 15

**Run 110:**
- Pareto front size: 1
- Consensus features: 1
- Exploratory features: 15

**Run 115:**
- Pareto front size: 1
- Consensus features: 1
- Exploratory features: 15

**Run 120:**
- Pareto front size: 1
- Consensus features: 1
- Exploratory features: 15

**Run 125:**
- Pareto front size: 1
- Consensus features: 1
- Exploratory features: 15

**Run 130:**
- Pareto front size: 1
- Consensus features: 1
- Exploratory features: 15

**Run 135:**
- Pareto front size: 1
- Consensus features: 1
- Exploratory features: 15

**Run 140:**
- Pareto front size: 1
- Consensus features: 1
- Exploratory features: 15

**Run 145:**
- Pareto front size: 1
- Consensus features: 1
- Exploratory features: 15

**Run 150:**
- Pareto front size: 1
- Consensus features: 1
- Exploratory features: 15

**Run 155:**
- Pareto front size: 1
- Consensus features: 1
- Exploratory features: 15

**Run 160:**
- Pareto front size: 1
- Consensus features: 1
- Exploratory features: 15

**Run 165:**
- Pareto front size: 1
- Consensus features: 1
- Exploratory features: 15

**Run 170:**
- Pareto front size: 1
- Consensus features: 1
- Exploratory features: 15

**Run 175:**
- Pareto front size: 2
- Consensus features: 1
- Exploratory features: 15

**Run 180:**
- Pareto front size: 2
- Consensus features: 1
- Exploratory features: 16

**Run 185:**
- Pareto front size: 2
- Consensus features: 1
- Exploratory features: 16

**Run 190:**
- Pareto front size: 2
- Consensus features: 1
- Exploratory features: 16

**Run 195:**
- Pareto front size: 2
- Consensus features: 1
- Exploratory features: 16

**Run 200:**
- Pareto front size: 2
- Consensus features: 1
- Exploratory features: 15

**Run 205:**
- Pareto front size: 2
- Consensus features: 1
- Exploratory features: 15

**Run 210:**
- Pareto front size: 2
- Consensus features: 1
- Exploratory features: 15

**Run 215:**
- Pareto front size: 2
- Consensus features: 1
- Exploratory features: 15

**Run 220:**
- Pareto front size: 2
- Consensus features: 1
- Exploratory features: 15

**Run 225:**
- Pareto front size: 2
- Consensus features: 1
- Exploratory features: 15

**Run 230:**
- Pareto front size: 2
- Consensus features: 1
- Exploratory features: 15

**Run 235:**
- Pareto front size: 2
- Consensus features: 1
- Exploratory features: 15

**Run 240:**
- Pareto front size: 2
- Consensus features: 1
- Exploratory features: 15

**Run 245:**
- Pareto front size: 2
- Consensus features: 1
- Exploratory features: 15

**Run 250:**
- Pareto front size: 2
- Consensus features: 1
- Exploratory features: 15

**Run 255:**
- Pareto front size: 2
- Consensus features: 1
- Exploratory features: 15

**Run 260:**
- Pareto front size: 2
- Consensus features: 1
- Exploratory features: 15

**Run 265:**
- Pareto front size: 2
- Consensus features: 1
- Exploratory features: 15

**Run 270:**
- Pareto front size: 2
- Consensus features: 1
- Exploratory features: 15

**Run 275:**
- Pareto front size: 2
- Consensus features: 1
- Exploratory features: 15

**Run 280:**
- Pareto front size: 2
- Consensus features: 1
- Exploratory features: 15

**Run 285:**
- Pareto front size: 2
- Consensus features: 1
- Exploratory features: 16

**Run 290:**
- Pareto front size: 2
- Consensus features: 1
- Exploratory features: 16

**Run 295:**
- Pareto front size: 2
- Consensus features: 1
- Exploratory features: 16

**Run 300:**
- Pareto front size: 2
- Consensus features: 1
- Exploratory features: 16

**Run 305:**
- Pareto front size: 2
- Consensus features: 1
- Exploratory features: 16

**Run 310:**
- Pareto front size: 2
- Consensus features: 1
- Exploratory features: 16

**Run 315:**
- Pareto front size: 2
- Consensus features: 1
- Exploratory features: 16

**Run 320:**
- Pareto front size: 2
- Consensus features: 1
- Exploratory features: 16

**Run 325:**
- Pareto front size: 2
- Consensus features: 1
- Exploratory features: 16

**Run 330:**
- Pareto front size: 2
- Consensus features: 1
- Exploratory features: 16

**Run 335:**
- Pareto front size: 2
- Consensus features: 1
- Exploratory features: 16

**Run 340:**
- Pareto front size: 2
- Consensus features: 1
- Exploratory features: 16

**Run 345:**
- Pareto front size: 2
- Consensus features: 1
- Exploratory features: 16

**Run 350:**
- Pareto front size: 2
- Consensus features: 1
- Exploratory features: 16

**Run 355:**
- Pareto front size: 2
- Consensus features: 1
- Exploratory features: 16

**Run 360:**
- Pareto front size: 2
- Consensus features: 1
- Exploratory features: 15

**Run 365:**
- Pareto front size: 2
- Consensus features: 1
- Exploratory features: 15

**Run 370:**
- Pareto front size: 2
- Consensus features: 1
- Exploratory features: 15

**Run 375:**
- Pareto front size: 2
- Consensus features: 1
- Exploratory features: 15

**Run 380:**
- Pareto front size: 2
- Consensus features: 1
- Exploratory features: 15

**Run 385:**
- Pareto front size: 2
- Consensus features: 1
- Exploratory features: 15

**Run 390:**
- Pareto front size: 2
- Consensus features: 1
- Exploratory features: 15

**Run 395:**
- Pareto front size: 2
- Consensus features: 1
- Exploratory features: 15

**Run 400:**
- Pareto front size: 2
- Consensus features: 1
- Exploratory features: 15

**Run 405:**
- Pareto front size: 2
- Consensus features: 1
- Exploratory features: 16

**Run 410:**
- Pareto front size: 2
- Consensus features: 1
- Exploratory features: 15

**Run 415:**
- Pareto front size: 2
- Consensus features: 1
- Exploratory features: 15

**Run 420:**
- Pareto front size: 2
- Consensus features: 1
- Exploratory features: 16

**Run 425:**
- Pareto front size: 2
- Consensus features: 1
- Exploratory features: 16

**Run 430:**
- Pareto front size: 2
- Consensus features: 1
- Exploratory features: 16

**Run 435:**
- Pareto front size: 2
- Consensus features: 1
- Exploratory features: 16

**Run 440:**
- Pareto front size: 2
- Consensus features: 1
- Exploratory features: 16

**Run 445:**
- Pareto front size: 2
- Consensus features: 1
- Exploratory features: 16

**Run 450:**
- Pareto front size: 3
- Consensus features: 1
- Exploratory features: 16

**Run 455:**
- Pareto front size: 3
- Consensus features: 1
- Exploratory features: 16

**Run 460:**
- Pareto front size: 3
- Consensus features: 1
- Exploratory features: 15

**Run 465:**
- Pareto front size: 3
- Consensus features: 1
- Exploratory features: 15

**Run 470:**
- Pareto front size: 3
- Consensus features: 1
- Exploratory features: 15

**Run 475:**
- Pareto front size: 3
- Consensus features: 1
- Exploratory features: 16

**Run 480:**
- Pareto front size: 3
- Consensus features: 1
- Exploratory features: 16

**Run 485:**
- Pareto front size: 3
- Consensus features: 1
- Exploratory features: 16

**Run 490:**
- Pareto front size: 3
- Consensus features: 1
- Exploratory features: 16

**Run 495:**
- Pareto front size: 3
- Consensus features: 1
- Exploratory features: 16

**Run 500:**
- Pareto front size: 3
- Consensus features: 1
- Exploratory features: 16


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

- `all_trees.csv`: Complete list of all 500 generated trees
- `feature_frequency.csv`: Feature frequency analysis with classifications
- `pareto_front.csv`: Trees on the Pareto frontier
- `stability_analysis.csv`: Stability metrics by run batch
- `results.json`: All data in JSON format for programmatic access

