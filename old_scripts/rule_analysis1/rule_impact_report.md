# Rule Impact Analysis Report

**Generated:** 2026-04-01 14:54:32  
**Dataset:** /Users/hmestes/gits/moot/optimize/financial_data/BankChurners.csv  
**Total Rules Extracted:** 291  
**Total Rule Occurrences:** 451

---

## Executive Summary

This analysis extracts individual decision rules from 50 EZR tree runs and ranks them by **implementation impact**.

### Key Innovation: Nested Rules

Rules can be **nested** (hierarchical conditions combined with AND):

```
BROAD RULE:
  (card_Category == Silver)
  → Affects 13 rows, win 30

NESTED RULE (more specific):
  (card_Category == Silver) AND (education_Level == College)
  → Affects 5 rows, win 79

DEEPLY NESTED RULE (very specific):
  (card_Category == Silver) AND (education_Level == College) AND (Total_Trans_Ct > 56)
  → Affects 1 row, win 88
```

**The trade-off:**
- Broad rules: More people, modest improvement
- Nested rules: Fewer people, stronger improvement

Both have value! Stakeholders pick different depths based on priorities.

---

## Top 10 Rules by Impact (Including Nested)

| Rank | Rule | Specificity | Coverage | Impact | Recommendation |
|------|------|-------------|----------|--------|-----------------|
| 1 | `(Avg_Utilization_Ratio > 0) AND (Avg_Utilization_Ratio ...` | NESTED (2 conditions) | 23.6% | 7.73 | ⭐ EASY WIN |
| 2 | `(Avg_Utilization_Ratio <= 0.094) AND (Avg_Utilization_R...` | NESTED (2 conditions) | 13.3% | 6.11 | ⭐ EASY WIN |
| 3 | `(Avg_Utilization_Ratio <= 0.138) AND (Avg_Utilization_R...` | NESTED (2 conditions) | 17.7% | 6.05 | ⭐ EASY WIN |
| 4 | `(Total_Trans_Ct > 92)` | BROAD | 11.8% | 5.93 | ⭐ EASY WIN |
| 5 | `(Avg_Utilization_Ratio <= 0.146) AND (Avg_Utilization_R...` | NESTED (2 conditions) | 20.7% | 5.90 | ⭐ EASY WIN |
| 6 | `(Avg_Utilization_Ratio > 0) AND (Avg_Utilization_Ratio ...` | NESTED (2 conditions) | 13.3% | 5.74 | ⭐ EASY WIN |
| 7 | `(Customer_Age > 48)` | BROAD | 22.1% | 5.45 | ⭐ EASY WIN |
| 8 | `(Avg_Utilization_Ratio <= 0.094)` | BROAD | 22.1% | 5.45 | ⭐ EASY WIN |
| 9 | `(card_Category == Silver)` | BROAD | 11.6% | 5.43 | ⭐ EASY WIN |
| 10 | `(Avg_Utilization_Ratio > 0)` | BROAD | 29.2% | 5.24 | ⭐ EASY WIN |


---

## Understanding Nested Rules (AND Conditions)

### What are Nested Rules?

From EZR tree structure:
```
if card_Category == Silver
  |  if education_Level == College
    |  |  if Total_Trans_Ct > 56
```

This is extracted as a single nested rule:
```
(card_Category == Silver) AND (education_Level == College) AND (Total_Trans_Ct > 56)
```

### Why Nesting Matters

**Broad Rule:**
- `(card_Category == Silver)` → 13 people, modest win
- Easy to implement (1 condition)
- Affects many customers

**Nested Rule:**
- `(card_Category == Silver) AND (education_Level == College)` → 5 people, higher win
- Slightly harder to implement (2 conditions)
- Targets a specific segment

**Deep Nested Rule:**
- `(card_Category == Silver) AND (education_Level == College) AND (Total_Trans_Ct > 56)` → 1 person, highest win
- Complex to implement (3 conditions)
- Hyper-targeted personalization

### When to Use Each

**Stakeholder Tim (Maximize Performance):**
- Wants to implement deeply nested rules
- Willing to add complexity for better accuracy
- Strategy: Build all nested rules

**Stakeholder Abi (Minimize Complexity):**
- Wants broad, simple rules
- Prefers rules with 1-2 conditions
- Strategy: Implement only BROAD rules

**Stakeholder Pat (Balance):**
- Wants moderately nested rules
- Sweet spot: 2-3 conditions with good impact
- Strategy: Implement BROAD + NESTED (2 conditions)

---

## Deployment Strategy by Rule Specificity

### Tier 0: Foundation (BROAD Rules - 1 Condition)


**Rule:** `(Total_Trans_Ct > 92)`
- Coverage: 11.8%
- Average Win: 51.0
- Impact Score: 5.93
- **Action:** Deploy immediately, no question


**Rule:** `(Customer_Age > 48)`
- Coverage: 22.1%
- Average Win: 25.0
- Impact Score: 5.45
- **Action:** Deploy immediately, no question


**Rule:** `(Avg_Utilization_Ratio <= 0.094)`
- Coverage: 22.1%
- Average Win: 25.0
- Impact Score: 5.45
- **Action:** Deploy immediately, no question


**Rule:** `(card_Category == Silver)`
- Coverage: 11.6%
- Average Win: 47.7
- Impact Score: 5.43
- **Action:** Deploy immediately, no question


**Rule:** `(Avg_Utilization_Ratio > 0)`
- Coverage: 29.2%
- Average Win: 18.2
- Impact Score: 5.24
- **Action:** Deploy immediately, no question


### Tier 1: Easy Wins (NESTED Rules - 2-3 Conditions)

These add specificity and often higher accuracy.


**Rule:** `(Avg_Utilization_Ratio > 0) AND (Avg_Utilization_Ratio <= 0.1)`
- Conditions: 2
- Coverage: 23.6%
- Average Win: 47.0
- Impact Score: 7.73
- **Action:** Add after foundation for higher accuracy


**Rule:** `(Avg_Utilization_Ratio <= 0.094) AND (Avg_Utilization_Ratio > 0)`
- Conditions: 2
- Coverage: 13.3%
- Average Win: 66.0
- Impact Score: 6.11
- **Action:** Add after foundation for higher accuracy


**Rule:** `(Avg_Utilization_Ratio <= 0.138) AND (Avg_Utilization_Ratio > 0.036)`
- Conditions: 2
- Coverage: 17.7%
- Average Win: 49.0
- Impact Score: 6.05
- **Action:** Add after foundation for higher accuracy


**Rule:** `(Avg_Utilization_Ratio <= 0.146) AND (Avg_Utilization_Ratio > 0)`
- Conditions: 2
- Coverage: 20.7%
- Average Win: 41.0
- Impact Score: 5.90
- **Action:** Add after foundation for higher accuracy


**Rule:** `(Avg_Utilization_Ratio > 0) AND (Avg_Utilization_Ratio <= 0.137)`
- Conditions: 2
- Coverage: 13.3%
- Average Win: 62.0
- Impact Score: 5.74
- **Action:** Add after foundation for higher accuracy


### Tier 2: Refinements (DEEPLY NESTED Rules - 4+ Conditions)

High accuracy but narrow scope. Watch diminishing returns.

- `(Avg_Utilization_Ratio <= 0.146) AND (Avg_Utilization_Ratio > 0) AND (...` (Impact: 2.53, Coverage: 8.9%)
- `(Avg_Utilization_Ratio > 0) AND (Avg_Utilization_Ratio <= 0.094) AND (...` (Impact: 2.44, Coverage: 5.9%)
- `(Avg_Utilization_Ratio <= 0.125) AND (Avg_Utilization_Ratio > 0) AND (...` (Impact: 2.14, Coverage: 8.9%)


### Rules to Skip

Avoid rules with negative impact regardless of nesting depth.

- `(Customer_Age > 48) AND (Avg_Utilization_Ratio > 0.174) AND (CLIENTNUM...` (Avg Win: -1.0) ❌
- `(income_Category == $60K - $80K) AND (Avg_Utilization_Ratio > 0.102)...` (Avg Win: -1.0) ❌
- `(Total_Trans_Ct <= 71) AND (income_Category == $60K - $80K)...` (Avg Win: -2.0) ❌
- `(education_Level == Graduate) AND (Customer_Age > 49)...` (Avg Win: -2.0) ❌
- `(card_Category == Blue) AND (education_Level == Graduate) AND (Naive_B...` (Avg Win: -2.0) ❌


---

## Stakeholder Alignment Story (With Nested Rules)

### Tim (Engineer - Wants Best Performance)

"I want to implement nested rules aggressively:

- **Tier 0**: All BROAD rules (1 condition) → foundation
- **Tier 1**: All NESTED rules (2-3 conditions) → +accuracy
- **Tier 2**: DEEPLY NESTED rules (4+ conditions) → squeeze the last gains

This maximizes accuracy even if it adds complexity. I can handle it."

### Abi (PM - Wants Simplicity)

"I want only simple rules:

- **Tier 0**: BROAD rules only (1 condition) → easy to explain
- Skip everything nested

This ships fast, stays simple, remains interpretable. The accuracy is good enough."

### Pat (Balance - Wants Best ROI)

"I want the sweet spot:

- **Tier 0**: All BROAD rules (1 condition) → foundation
- **Tier 1**: NESTED rules with 2 conditions only → good ROI
- Skip: 3+ conditions → diminishing returns

This balances accuracy gains against implementation complexity."

---

## Key Insights

1. **Broad vs. Nested Trade-off**: Stakeholders naturally diverge on how deep to nest rules
2. **Same Rules, Different Depths**: Everyone agrees on Tier 0 (1 condition), diverge on Tier 1+
3. **Measurable Impact**: Each nesting level has quantifiable impact score
4. **Clear Tiers**: Natural breakpoints where diminishing returns begin

---

## Cumulative Improvement (Nested Version)

See `deployment_roadmap.csv` for how accuracy improves as you add:
- All BROAD rules → X% accuracy
- BROAD + NESTED (2 cond) → Y% accuracy  
- BROAD + NESTED (2-3 cond) → Z% accuracy
- Everything → W% accuracy

Stakeholders can see exactly where the diminishing returns kick in.

---

## For Your Research

### Tier 1: Individual Choice

Show rules at different nesting depths:

```
Rule A: (card_Category == Silver)                                     [1 condition]
Rule B: (card_Category == Silver) AND (education_Level == College)   [2 conditions]
Rule C: (card_Category == Silver) AND ... AND (Total_Trans_Ct > 56) [3 conditions]
```

"Which depth would you implement?"

### Tier 2: Nested Rule Explanation

Show the deployment roadmap with nesting depths marked.

### Tier 3: LLM Explanations

Use Claude to explain why different stakeholders prefer different nesting depths based on their values.

---

## Files Generated

- `rules_ranked_by_impact.csv`: All rules (broad and nested) sorted by impact
- `deployment_roadmap.csv`: Cumulative path showing nesting levels
- `rules_all_extracted.csv`: Complete rule database with condition counts
- `rule_impact_report.md`: This report

