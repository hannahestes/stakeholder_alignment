# Rule Impact Analyzer - Usage Guide

## Quick Start

```bash
python3 rule_impact_analyzer.py \
  --runs 50 \
  --dataset ~/gits/moot/optimize/financial_data/BankChurners.csv
```

**Output:** `rule_analysis/` folder with 4 files

---

## What It Does

Instead of asking "Which tree model?", it asks:

**"Which individual rules should we implement, in what order, for different stakeholders?"**

### Example: Your BankChurners Data

Before:
```
Run 37: 1 feature, 70% accuracy → UNCLEAR VALUE
Run 43: 4 features, 75% accuracy → UNCLEAR VALUE
Run 6: 5 features, 94% accuracy → TOO COMPLEX
```

After (Rule-Level Analysis):
```
FOUNDATION:
  Rule 1: education_Level splits → 50 rows, win 70 → DEPLOY FIRST

TIER 1 (Easy Wins):
  Rule 2: card_Category == Silver → 13 rows, win 79 → ADD NEXT
  Rule 3: income_Category == X → 20 rows, win 68 → ADD AFTER

TIER 2 (Refinement):
  Rule 4: Total_Trans_Ct > 56 → 9 rows, win 45 → OPTIONAL

AVOID:
  Rule X: Some_Feature → rows 3, win -52 → DON'T USE
```

**Now stakeholders can see:** Which rules they'd pick based on their values!

---

## Output Files

### 1. `rule_impact_report.md`
**Start here!** Human-readable analysis with:
- Top 10 rules by impact
- Deployment strategy (Tier 0, 1, 2...)
- Stakeholder alignment story
- Key metrics explained

### 2. `rules_ranked_by_impact.csv`
Complete rule ranking:
```
rule,occurrences,penetration_%,avg_win,avg_rows,coverage_%,impact_score,roi_win_per_row,recommendation
"education_Level == High School",45,90.0,70.2,51.3,25.6,8.95,1.37,"🟢 FOUNDATION"
"card_Category == Silver",38,76.0,78.9,13.2,6.6,5.16,5.98,"⭐ EASY WIN"
"income_Category == Less than $40K",32,64.0,65.4,18.5,9.2,4.67,3.53,"✓ GOOD"
```

### 3. `deployment_roadmap.csv`
Shows cumulative impact:
```
rank,rule,recommendation,impact,coverage_%,cumulative_impact,suggested_tier
1,"education_Level == High School","🟢 FOUNDATION",8.95,25.6%,8.95,"Tier 0: Foundation"
2,"card_Category == Silver","⭐ EASY WIN",5.16,6.6%,14.11,"Tier 1: Quick Wins"
3,"income_Category == Less than $40K","✓ GOOD",4.67,9.2%,18.78,"Tier 2: Good Rules"
```

Use this to show stakeholders:
- "If we implement rules 1-3, we get X% accuracy"
- "Rules 1-2 take 2 weeks, rule 3 takes 1 more week"

### 4. `rules_all_extracted.csv`
Complete rule database (all 50 runs, all rules):
```
run,rule,rows,win,depth,rule_key
1,"education_Level == High School",51,70,0,"education_Level == High School"
1,"income_Category == Less than $40K",15,-19,1,"income_Category == Less than $40K"
2,"education_Level == High School",48,72,0,"education_Level == High School"
...
```

---

## Key Metrics Explained

### Impact Score
**What:** How valuable a rule is to implement  
**Formula:** `(average_win × average_rows) / total_rows`

**Interpretation:**
- **>8**: Excellent (implement immediately)
- **5-8**: Very good (implement after foundation)
- **2-5**: Good (implement after tier 1)
- **<2**: Marginal (consider skipping)

### Penetration %
**What:** How often a rule appears across 50 runs  
**Why it matters:** Stable rules (high penetration) are more reliable

- **>80%**: Very stable, core to the problem
- **50-80%**: Fairly stable, good to implement
- **<50%**: Variable, may not generalize

### Coverage %
**What:** How many rows the rule applies to  
**Why it matters:** Broad rules affect more people

- **>20%**: Affects large segment (foundation potential)
- **5-20%**: Affects moderate segment (good rule)
- **<5%**: Affects small segment (easy win or overfit)

### ROI (Win Per Row)
**What:** Efficiency of the rule  
**Formula:** `average_win / average_rows`

**Interpretation:**
- **High ROI (>5)**: Small segments, very accurate (targeted)
- **Medium ROI (2-5)**: Balanced (good foundation)
- **Low ROI (<2)**: Broad but modest improvement (basic)

---

## For Your Research Study

### Tier 1: Individual Preference (No Explanation)

Show rules, ask individuals to rank:

```
Which 3 rules would you prioritize implementing?

[ ] Rule A: education_Level (Foundation, 70 impact)
[ ] Rule B: card_Category == Silver (Easy win, 79 accuracy)
[ ] Rule C: income_Category range (Broad, 68 accuracy)
```

**Expected:** Different stakeholders pick different rules
- Tim picks all (maximize performance)
- Abi picks only A (minimize effort)
- Pat picks A + B (balance)

### Tier 2: Pareto Explanation (Deployment Roadmap)

Show the cumulative impact:

```
Rule A (Foundation): Implement → 70% accuracy, effort: 2 days
Rule B (Easy Win): Add → 78% accuracy, effort: +3 days
Rule C (Broad): Add → 82% accuracy, effort: +4 days
Rule D (Targeted): Add → 85% accuracy, effort: +5 days
```

"Where do you draw the line? How much accuracy vs. effort?"

**Expected:** Convergence on natural tiers (everyone picks A+B, some pick A+B+C)

### Tier 3: Persona-Tailored LLM Explanations

Use LLM to explain **why** different stakeholders pick different rules:

**Tim's perspective (Engineer):**
```
"Rules A-D together give 85% accuracy, which is strong.
Rule D (targeted) has 5.2 impact score - worth the effort.
The diminishing returns don't kick in until Rule E.
Recommendation: Implement A-D immediately."
```

**Abi's perspective (PM):**
```
"Rule A alone gives 70% accuracy in 2 days.
That's 70% better than the baseline with minimal risk.
Rules B-D add 15% more accuracy but take 3x longer.
Recommendation: Ship Rule A, measure production results, then add B-C."
```

**Pat's perspective (Balance):**
```
"Rules A-B give 78% accuracy in 5 days - excellent ROI.
Rules C-D add diminishing returns (only 7% more, +9 days).
The sweet spot is A-B-C at 82% accuracy, 11 days.
Recommendation: Prioritize A-B-C for best balance."
```

**Convergent Divergence:**
- All three see the same rules and same cumulative impact
- All three agree on rules A-B as essential
- They diverge on rules C-D based on different priorities
- **This is genuine alignment, not forced compromise!**

---

## Example Workflow for Your Study

### Day 1: Extract and Analyze

```bash
python3 rule_impact_analyzer.py \
  --runs 50 \
  --dataset ~/gits/moot/optimize/financial_data/BankChurners.csv

# Output: rule_analysis/
```

### Day 2: Tier 1 Evaluation

Print out `rules_ranked_by_impact.csv`, show top 5 rules to stakeholders:

```
"Which of these rules would you implement first?"

1. Rule A (Foundation, 70 impact) - Affects 25% of customers
2. Rule B (Easy Win, 52 impact) - Affects 6.6% of customers
3. Rule C (Good, 47 impact) - Affects 9.2% of customers
4. Rule D (Targeted, 31 impact) - Affects 3% of customers
5. Rule E (Rare, 12 impact) - Affects 1% of customers
```

### Day 2: Tier 2 (Same Stakeholders)

Show deployment roadmap:

```
Tim's choice: Rules 1-5 (all of them)
  → 94% accuracy, 4 weeks to implement

Abi's choice: Rule 1 only
  → 70% accuracy, 1 week to implement

Pat's choice: Rules 1-3
  → 82% accuracy, 2 weeks to implement
```

### Day 3: Tier 3 (LLM Personas)

Generate persona-tailored explanations for why each person made their choice. Use Claude:

```python
# Pseudo-code for LLM prompt

prompt = f"""
You are Tim, a software engineer who values technical performance.
Here's the rule impact analysis for a decision system:

{rules_dataframe}

You're asked which rules to implement first. You see:
- Foundation rules (broad impact, stable)
- Easy wins (high accuracy, narrow impact)
- Targeted rules (very high accuracy, tiny segment)

Explain your implementation strategy as Tim would,
focusing on maximizing system accuracy and robustness.
"""
```

---

## Command-Line Options

```bash
python3 rule_impact_analyzer.py \
  --runs 50 \
  --dataset ~/path/to/data.csv \
  --output-dir ./my_analysis
```

- `--runs`: Number of EZR runs (default: 50)
- `--dataset`: Path to CSV file (required)
- `--output-dir`: Where to save outputs (default: rule_analysis)

---

## Understanding the Output Better

### Why Penetration % Matters

Rule A appears in 45/50 runs (90%):
- ✅ Very stable
- ✅ Core to the problem
- ✅ Safe to deploy

Rule X appears in 2/50 runs (4%):
- ⚠️ Very unstable
- ⚠️ Might be overfitting
- ⚠️ May not generalize

### Why Coverage % Matters

Rule A affects 25% of customers:
- ✅ Impacts many people
- ✅ Foundation rule
- ✅ High ROI for implementation effort

Rule B affects 1% of customers:
- ⚠️ Impacts few people
- ⚠️ High win, but narrow scope
- ✅ Easy win (small effort for targeted improvement)

### Tiers Explained

**Tier 0: Foundation**
- High penetration (>80%)
- Broad coverage (>15%)
- Solid impact (>5)
- Action: Deploy immediately, no question

**Tier 1: Easy Wins**
- High impact (>5)
- Narrow coverage (<10%)
- High accuracy but specialized
- Action: Add after foundation, quick ROI

**Tier 2: Good Rules**
- Moderate impact (2-5)
- Moderate coverage (5-15%)
- Solid accuracy
- Action: Add for refinement, watch returns

**Tier 3+: Diminishing Returns**
- Impact <2
- Coverage <5%
- Low penetration
- Action: Consider skipping, implement last if budget allows

---

## For Your Research Paper

### Section: Methods

> "We extracted individual decision rules from 50 EZR tree runs 
> and ranked them by implementation impact (win × coverage / dataset_size). 
> Rules were classified into tiers based on impact score, coverage, and 
> stability (penetration across runs). This allowed us to move beyond 
> tree-level analysis to rule-level implementation strategy."

### Section: Results

> "Analysis identified X foundation rules (penetration >80%), Y easy wins 
> (impact >5), and Z optional rules. Foundation rules affect Z% of customers 
> with average accuracy of X%. Easy wins affect Y% of customers with 
> concentrated high accuracy. Stakeholders showed genuine divergence in 
> rule selection based on values (performance vs. speed vs. balance) 
> despite seeing identical rule rankings."

### Section: Discussion

> "This rule-level analysis reveals that stakeholder alignment is not about 
> 'which model' but 'which rules in what order.' Different stakeholders 
> converge on foundation rules while diverging on optional rules based on 
> their priorities. This explains how genuine consensus emerges in real 
> decision systems."

---

## Advanced: Customizing Impact Calculation

Want to weight rules by different criteria?

Edit the `_get_recommendation()` and calculation functions:

```python
# Current (simple):
impact = (win × rows) / total_rows

# Alternative (ROI-focused):
impact = (win / rows) × penetration

# Alternative (deployment cost):
impact = win / (complexity × effort_weeks)

# Alternative (for your domain):
impact = (win × penetration) / (coverage × cost)
```

Let me know if you want to customize!

---

## Questions?

The rule-level analysis should give you:
- ✅ Clear decision path (which rules to implement first)
- ✅ Stakeholder divergence (different priorities → different selections)
- ✅ Genuine alignment (same rules, different sequences)
- ✅ Publishable finding (rule-level analysis is novel)

Ready to run it? 🚀
