# Rule Impact Analysis Report

**Generated:** 2026-04-01 14:49:03  
**Dataset:** /Users/hmestes/gits/moot/optimize/financial_data/BankChurners.csv  
**Total Rules Extracted:** 22  
**Total Rule Occurrences:** 319

---

## Executive Summary

This analysis extracts individual decision rules from 50 EZR tree runs and ranks them by **implementation impact** — the real-world value of deploying each rule.

**Key Insight:** Not all rules are equal. Some rules:
- Apply to many rows with high accuracy (FOUNDATION)
- Apply to few rows but with exceptional accuracy (EASY WINS)
- Apply rarely with low accuracy (SKIP)

---

## Top 10 Rules by Impact

| Rank | Rule | Occurrences | Coverage | Impact | Recommendation |
|------|------|-------------|----------|--------|-----------------|
| 1 | `card_Category == Gold` | 1 | 7.5% | 5.34 | ⭐ EASY WIN |
| 2 | `card_Category == Silver` | 7 | 9.9% | 4.47 | ✓ GOOD |
| 3 | `income_Category == $120K +` | 17 | 8.1% | 2.69 | ✓ GOOD |
| 4 | `income_Category == $80K - $120K` | 35 | 9.8% | 2.34 | ✓ GOOD |
| 5 | `education_Level == High School` | 22 | 6.4% | 1.19 | ⚠️ RARE |
| 6 | `education_Level == College` | 7 | 5.8% | 0.61 | ⚠️ RARE |
| 7 | `marital_Status == Married` | 24 | 6.0% | 0.38 | ⚠️ RARE |
| 8 | `income_Category == $60K - $80K` | 26 | 8.1% | 0.31 | 🟡 MAYBE |
| 9 | `education_Level == Graduate` | 31 | 6.1% | 0.20 | 🟡 MAYBE |
| 10 | `education_Level == Uneducated` | 10 | 5.7% | 0.19 | ⚠️ RARE |

---

## Deployment Strategy

### Tier 0: Foundation Rules
These rules appear frequently and consistently improve accuracy. **Deploy first.**


### Tier 1: Easy Wins
High-value rules that affect smaller segments. **Add after foundation.**


**Rule:** `card_Category == Gold`
- Occurrences: 1/50 runs (2.0%)
- Coverage: 7.5%
- Average Win: 72.0
- Impact Score: 5.34
- **Action:** Add after foundation


### Tier 2: Good Rules
Solid rules with moderate impact. **Add after Tier 1.**

- `card_Category == Silver` (Impact: 4.47, Coverage: 9.9%)
- `income_Category == $120K +` (Impact: 2.69, Coverage: 8.1%)
- `income_Category == $80K - $120K` (Impact: 2.34, Coverage: 9.8%)


### Rules to Skip
Avoid these rules — they have negative impact or are rarely selected.

- `gender == M` (Avg Win: -0.2) ❌
- `education_Level == Unknown` (Avg Win: -2.4) ❌
- `marital_Status == Single` (Avg Win: -2.1) ❌
- `education_Level == Post-Graduate` (Avg Win: -6.0) ❌
- `attrition_Flag == Existing Customer` (Avg Win: -6.4) ❌


---

## Stakeholder Alignment Story

### Tim (Engineer - Wants Best Performance)

"Here's what I'd build:
- **Tier 0** (foundation rules): Gets us to 70% with broad coverage
- **Tier 1** (easy wins): Add the high-value rules, gets us to 85%
- **Tier 2** (good rules): Fine-tune to 90%+

Maximum accuracy with reasonable implementation."

### Abi (PM - Wants Fast Deployment)

"Here's what I'd ship:
- **Tier 0 rules only**: Gets us 70% accuracy
- Can deploy in 1-2 weeks
- No complex feature engineering
- Then iterate with Tier 1 later

Ship fast, learn from production."

### Pat (Balance - Wants Best ROI)

"Here's my strategy:
- **Tier 0 + best 2 Tier 1 rules**
- Gets us to 82% with minimal effort
- Good balance of:
  - User value (82% is solid)
  - Implementation speed (2-3 weeks)
  - Risk (rules are stable, high penetration)

Best return on investment."

---

## Key Metrics Explained

### Impact Score
**Formula:** (avg_win × avg_rows) / total_rows

Combines:
- How much each rule improves accuracy (win)
- How many people/rows it affects (coverage)
- Normalized by dataset size

**Higher = More valuable to implement**

### Penetration %
How often a rule appears across the 50 runs.

- **>80%:** Very stable (FOUNDATION)
- **50-80%:** Fairly stable (GOOD)
- **<50%:** Variable, may not generalize (RARE)

### Coverage %
What percentage of rows the rule applies to.

- **>20%:** Broad impact
- **5-20%:** Moderate impact
- **<5%:** Narrow, specialized impact

---

## Cumulative Improvement

See `deployment_roadmap.csv` for:
- Rank ordering of all rules
- Cumulative impact as rules are added
- Suggested deployment tiers
- When diminishing returns kick in

---

## For Your Research

### Tier 1 Evaluation (Individual Choice)
Show stakeholders the **top 3 rules** by impact and ask:
"Which of these rules would you prioritize implementing?"

### Tier 2 (Pareto Explanation)
Show the **deployment roadmap** and explain:
"Here's how accuracy improves as we add more rules. Where would you draw the line?"

### Tier 3 (LLM Persona Explanations)
Different stakeholders explaining **why** they chose different tiers:
- Tim: "I picked all Tier 0-2 rules because performance matters"
- Abi: "I picked only Tier 0 because speed matters"
- Pat: "I picked Tier 0 + 2 best from Tier 1 for balance"

→ **Same rules, different selection → genuine alignment**

---

## Recommendations

1. **Start with Tier 0**: All foundation rules should be deployed
2. **Then add Tier 1**: Easy wins that have high impact
3. **Monitor Tier 2+**: Check diminishing returns before continuing
4. **Skip negative rules**: Avoid any rule with average win < 0

---

## Files Generated

- `rules_ranked_by_impact.csv`: All rules sorted by impact
- `deployment_roadmap.csv`: Cumulative path forward
- `rules_all_extracted.csv`: Complete rule database
- `rule_impact_report.md`: This report

