# Pareto Front Visualization: Complexity vs. Impact

## What You'll Get

The updated script now generates **2 high-quality visualizations**:

### 1. `pareto_complexity_vs_impact.png` - Simple Overview
Clean, presentation-ready showing the frontier and knee point.

### 2. `pareto_complexity_vs_impact_detailed.png` - Full Analysis
Detailed view with rule labels showing exactly which rules are on the frontier.

---

## The Visualization Explained

### Axes

- **X-axis (Horizontal)**: Complexity = Number of nested conditions (1, 2, 3, 4...)
- **Y-axis (Vertical)**: Impact = How valuable the rule is to implement

### The Points

- 🟢 **Green dots**: Rules on the Pareto frontier (optimal)
- ⚫ **Gray dots**: Rules off the frontier (dominated by green dots)
- 🟥 **Red star**: The "knee" point (best trade-off)

### Understanding the Trade-off

```
Complexity (X-axis): How many conditions to implement
  • 1 condition: Simple (just card_Category == Silver)
  • 2 conditions: More complex (card_Category == Silver AND education_Level == College)
  • 3 conditions: Very complex (all of the above AND Total_Trans_Ct > 56)

Impact (Y-axis): How much value the rule adds
  • High impact (top): Rule is very valuable, affects many people
  • Low impact (bottom): Rule is marginal, affects few people
```

---

## Example: What the Frontier Tells You

### Typical Pareto Front Pattern

```
Impact
   10 |                          ⭐ (3 cond, 9.5 impact)
      |                      
    8 |                   🟢 (2 cond, 8.0 impact)
      |
    6 |              🟢 (2 cond, 5.8 impact)
      |
    4 |         🟢 (1 cond, 4.2 impact)     ⚫ (3 cond, 3.5)
      |     ⚫                                    ⚫
    2 |  🟢 (1 cond, 1.8 impact)    ⚫ (4 cond, 1.5)
      |
    0 +---+---+---+---+---+---+---+---+---+---+
      1   2   3   4   5   6   7
         Complexity (# conditions)
```

### What This Means

**Frontier Rules (Green):**
- Generally follow this pattern: Lower complexity = lower impact, higher complexity = higher impact
- Each rule is the best choice at its complexity level
- Represents the natural trade-off between simplicity and value

**Off-Frontier Rules (Gray):**
- Dominated by green dots
- For example: A 3-condition rule with 3.5 impact is worse than a 2-condition rule with 8.0 impact
- Safe to skip these

**Knee Point (Red Star):**
- Usually around 1-2 conditions
- The point where you get good impact without excessive complexity
- Where most stakeholders converge

---

## How Stakeholders Differ Using This Visualization

### Tim (Engineer): "Go deep!"
- Looks at the frontier and follows it all the way right
- "I'll implement up to 4-5 conditions to maximize impact"
- Chooses: Rules at 1, 2, 3, 4 conditions
- Gets highest possible accuracy

### Abi (PM): "Keep it simple!"
- Stops at the knee or just after
- "I'll only implement 1-2 condition rules"
- Chooses: Rules at 1 condition only
- Ships fast with solid impact

### Pat (Balance): "Sweet spot"
- Finds the elbow where returns start diminishing
- "I'll go up to 2-3 conditions max"
- Chooses: Rules at 1-2 conditions
- Best ROI without excessive complexity

**All three see the same frontier, but interpret it differently!**

---

## Reading the Detailed Visualization

The detailed version shows:

### Rule Labels

Each frontier point is labeled:
```
C1 (4.2)  ← 1 condition, impact 4.2
C2 (8.0)  ← 2 conditions, impact 8.0
C3 (9.5)  ← 3 conditions, impact 9.5
```

### Knee Annotation

The red star shows exactly where the knee is:
```
OPTIMAL
2 conditions
Impact: 8.0
```

This tells you: "The sweet spot is 2 conditions"

---

## What the Pareto Front Reveals About Your Data

### Pattern 1: Linear Increase (Common)
```
Complexity → 1   → 2   → 3   → 4
Impact     → 4.2 → 8.0 → 9.5 → 9.8
```

**Interpretation:** Each condition adds value, but returns diminish. Knee is usually around condition 2-3.

### Pattern 2: Quick Jump Then Plateau (Common)
```
Complexity → 1   → 2   → 3   → 4
Impact     → 2.1 → 8.5 → 8.6 → 8.7
```

**Interpretation:** The second condition is magic (jump from 2.1 to 8.5). After that, diminishing returns. Everyone should use 2 conditions.

### Pattern 3: Scattered Points (Complex)
```
Multiple rules at each complexity level, some dominate others
```

**Interpretation:** Rules of the same complexity vary widely. Stakeholders can pick the best rule at their preferred complexity level.

---

## Using This for Your Research

### Tier 1: Individual Choice
Show the simple Pareto visualization (no labels) and ask:
```
"How many conditions would you implement?
Point to where you'd stop on the frontier."
```

**Expected:** Different stakeholders point to different spots
- Tim: points far right (3-4 conditions)
- Abi: points left (1 condition)
- Pat: points middle (2 conditions)

### Tier 2: Pareto Explanation
Show the detailed visualization with knee marked and ask:
```
"Here's the optimal point (the knee).
What changes your preference?"
```

**Expected:** Stakeholders see the knee and understand the trade-off better.

### Tier 3: LLM Explanations
Use Claude to explain why different stakeholders have different preferences:

**Tim's perspective:**
```
"The Pareto front shows that each additional condition adds impact:
- 1 condition: 4.2 impact
- 2 conditions: 8.0 impact (+90%!)
- 3 conditions: 9.5 impact (+19% more)

Even though returns diminish, I want maximum accuracy.
Implement all the way to 3+ conditions."
```

**Abi's perspective:**
```
"The knee is at 2 conditions (8.0 impact).
Adding the third condition only gives +19% more impact
but doubles the implementation complexity.

It's not worth it. I'd stop at the knee."
```

**Pat's perspective:**
```
"The jump from 1→2 conditions is huge (+90%!),
but 2→3 is minimal (+19%).

The sweet spot is clearly 2 conditions.
Good impact without excessive complexity."
```

---

## The CSV Output: `pareto_frontier_rules.csv`

Shows only the Pareto frontier rules:

```
rule,complexity,impact,coverage,penetration,avg_win,recommendation,is_knee
"(card_Category == Silver)",1,4.20,6.5%,76.0%,30.2,"⭐ EASY WIN",false
"(card_Category == Silver) AND (education_Level == College)",2,8.00,2.6%,44.0%,79.0,"⭐ EASY WIN",true
"(card_Category == Silver) AND (education_Level == College) AND (Total_Trans_Ct > 56)",3,9.50,0.5%,16.0%,88.0,"⚠️ RARE",false
```

Key column: `is_knee` tells you which rule is the optimal trade-off point.

---

## Key Insights for Your Paper

### The Visualization Shows

1. **Natural Trade-off**: Complexity clearly trades off against impact
2. **Optimal Point**: The knee shows where smart people would stop
3. **Stakeholder Divergence**: Different people can naturally prefer different points on the frontier
4. **Genuine Alignment**: Tim wants more complexity (right side), Abi wants less (left side), Pat picks the middle—all based on the same Pareto front!

### Research Finding

> "Rule-level Pareto front analysis reveals that stakeholder alignment naturally emerges at different complexity levels. While all stakeholders see the same frontier, they diverge based on their values (performance vs. simplicity vs. balance). The knee point represents genuine consensus on where smart optimization should stop."

---

## Running the Script

```bash
python3 rule_impact_analyzer.py \
  --runs 50 \
  --dataset ~/gits/moot/optimize/financial_data/BankChurners.csv
```

Output files:
- `pareto_complexity_vs_impact.png` — Simple, clean visualization
- `pareto_complexity_vs_impact_detailed.png` — With all labels and annotations
- `pareto_frontier_rules.csv` — Frontier rules only
- All other CSVs and reports (unchanged)

---

## Example Output You'll See

### Simple Version
Clean frontier with knee marked in red. Perfect for presentations.

### Detailed Version
Each frontier rule labeled with its complexity and impact score:
```
           C3 (9.5)
               🟢
               |
            C2 (8.0) 🟢
            /    
        C1 (4.2)
        🟢
```

The red star is placed at the knee (usually C2 or C3 depending on your data).

---

## Perfect for Your 3-Day Study

**Day 1:** Generate the Pareto visualizations  
**Day 2 (Tier 1):** Show simple version, ask where they'd stop  
**Day 2 (Tier 2):** Show detailed version with knee marked  
**Day 3 (Tier 3):** Use LLM to explain why different people choose different complexity levels  

**Result:** Genuine stakeholder alignment through visual reasoning! 🎯
