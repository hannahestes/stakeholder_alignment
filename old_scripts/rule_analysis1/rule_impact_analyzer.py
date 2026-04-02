#!/usr/bin/env python3
"""
Rule Impact Analyzer for EZR Decision Trees
Extracts individual rules from EZR output and ranks them by implementation impact.

Usage:
    python3 rule_impact_analyzer.py --runs 50 --dataset BankChurners.csv

Outputs:
    - rules_extracted.csv: All rules with their metrics
    - rules_ranked_by_impact.csv: Rules sorted by impact score
    - deployment_roadmap.csv: Cumulative accuracy as rules are added
    - rule_impact_report.md: Human-readable analysis
"""

import subprocess
import re
import pandas as pd
import json
from pathlib import Path
from collections import defaultdict
from datetime import datetime

class RuleExtractor:
    def __init__(self, dataset_path, output_dir="rule_analysis"):
        self.dataset_path = dataset_path
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Storage for all rules across all runs
        self.all_rules = []
        self.rule_occurrences = defaultdict(lambda: {'count': 0, 'wins': [], 'rows': []})
        self.total_rows_per_run = {}
        
    def run_and_extract(self, n_runs=50):
        """Run EZR multiple times and extract all rules."""
        
        print(f"🚀 Running EZR {n_runs} times to extract rules...\n")
        
        for run_num in range(1, n_runs + 1):
            try:
                result = subprocess.run(
                    ["ezr", "-f", str(self.dataset_path)],
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                
                if result.returncode != 0:
                    print(f"⚠️  Run {run_num} failed")
                    continue
                
                # Extract rules from this run
                rules = self.extract_rules_from_output(result.stdout, run_num)
                self.all_rules.extend(rules)
                
                if run_num % 10 == 0:
                    print(f"  ✓ Completed {run_num} runs ({len(self.all_rules)} rules extracted)")
                    
            except Exception as e:
                print(f"⚠️  Error in run {run_num}: {e}")
                continue
        
        print(f"\n✅ Extraction complete: {len(self.all_rules)} rules found across {n_runs} runs\n")
    
    def extract_rules_from_output(self, output, run_num):
        """Parse EZR output and extract individual rules, including nested conditions.
        
        Handles hierarchical rules like:
          if card_Category == Silver
            |  if education_Level == College
              |  |  if Total_Trans_Ct > 56
        
        Combines into: (card_Category == Silver) AND (education_Level == College) AND (Total_Trans_Ct > 56)
        """
        
        rules = []
        lines = output.strip().split('\n')
        
        # Get total rows from last line
        if len(lines) >= 1:
            last_line = lines[-1].strip()
            parts = last_line.split()
            if len(parts) >= 2:
                try:
                    total_evals = int(parts[0])
                    final_win = int(parts[-1])
                    self.total_rows_per_run[run_num] = total_evals
                except ValueError:
                    pass
        
        # Parse tree structure, tracking rule paths
        rule_stack = []  # Stack of rules at each depth level
        
        for line in lines:
            # Skip header and final lines
            if line.startswith('#') or line.startswith('Used:') or line.startswith('Rank'):
                continue
            
            # Check for rule conditions
            if ' if ' in line and (' == ' in line or ' <= ' in line or ' > ' in line):
                # Extract: #rows, win, rule
                parts = line.split()
                
                try:
                    rows = int(parts[0])
                    win = int(parts[1])
                    
                    # Extract the rule part (everything after "if")
                    if_index = line.find(' if ')
                    rule_part = line[if_index+4:].strip().rstrip(';')
                    
                    # Calculate indentation level (number of '|' symbols)
                    indent_level = line.count('|')
                    
                    # Trim rule_stack to current depth (remove deeper rules)
                    rule_stack = rule_stack[:indent_level]
                    
                    # Add current rule to stack
                    rule_stack.append(rule_part)
                    
                    # Build combined rule (all conditions from root to here)
                    combined_rule = ' AND '.join(f"({r})" for r in rule_stack)
                    
                    rule_obj = {
                        'run': run_num,
                        'rule': combined_rule,  # Full nested rule as AND statement
                        'leaf_condition': rule_part,  # Just this condition
                        'rows': rows,
                        'win': win,
                        'depth': indent_level,
                        'num_conditions': len(rule_stack),
                        'rule_key': self._normalize_rule(combined_rule)
                    }
                    
                    rules.append(rule_obj)
                    
                    # Track occurrences
                    rule_key = rule_obj['rule_key']
                    self.rule_occurrences[rule_key]['count'] += 1
                    self.rule_occurrences[rule_key]['wins'].append(win)
                    self.rule_occurrences[rule_key]['rows'].append(rows)
                    
                except (ValueError, IndexError):
                    continue
        
        return rules
    
    def _normalize_rule(self, rule_str):
        """Normalize rule strings to identify duplicates."""
        # Remove extra spaces and semicolons
        normalized = rule_str.strip().rstrip(';')
        return normalized
    
    def calculate_impact_scores(self):
        """Calculate impact metrics for all extracted rules (including nested AND conditions)."""
        
        print("📊 Calculating impact scores...\n")
        
        impact_data = []
        avg_total_rows = sum(self.total_rows_per_run.values()) / len(self.total_rows_per_run) if self.total_rows_per_run else 100
        
        for rule_key, data in self.rule_occurrences.items():
            count = data['count']
            avg_win = sum(data['wins']) / len(data['wins']) if data['wins'] else 0
            avg_rows = sum(data['rows']) / len(data['rows']) if data['rows'] else 0
            
            # Impact score metrics
            # Nested rules (with AND conditions) have smaller sample sizes, so normalize by depth
            num_conditions = rule_key.count(' AND ') + 1
            depth_penalty = 1.0 / (num_conditions ** 0.5)  # Slight penalty for more complex rules
            
            impact_simple = ((avg_win * avg_rows) / (avg_total_rows + 1)) * depth_penalty
            coverage = (avg_rows / avg_total_rows) * 100
            
            # ROI: win per row (how efficient)
            roi = avg_win / max(avg_rows, 1)
            
            # Penetration: how many runs had this rule
            penetration = (count / 50) * 100
            
            # Specificity indicator: how targeted is this rule
            specificity = "BROAD" if num_conditions == 1 else f"NESTED ({num_conditions} conditions)"
            
            impact_data.append({
                'rule': rule_key,
                'conditions': num_conditions,
                'specificity': specificity,
                'occurrences': count,
                'penetration_%': f"{penetration:.1f}%",
                'avg_win': f"{avg_win:.1f}",
                'avg_rows': f"{avg_rows:.1f}",
                'coverage_%': f"{coverage:.1f}%",
                'impact_score': f"{impact_simple:.2f}",
                'roi_win_per_row': f"{roi:.2f}",
                'recommendation': self._get_recommendation(impact_simple, penetration, avg_win)
            })
        
        # Sort by impact score
        impact_df = pd.DataFrame(impact_data)
        impact_df['impact_score_num'] = pd.to_numeric(impact_df['impact_score'])
        impact_df = impact_df.sort_values('impact_score_num', ascending=False).drop('impact_score_num', axis=1)
        
        self.impact_df = impact_df
        return impact_df
    
    def _get_recommendation(self, impact, penetration, avg_win):
        """Get deployment recommendation based on metrics."""
        
        if avg_win < 0:
            return "❌ AVOID (negative)"
        elif penetration >= 80:
            return "🟢 FOUNDATION"
        elif impact >= 5:
            return "⭐ EASY WIN"
        elif impact >= 2:
            return "✓ GOOD"
        elif penetration >= 50:
            return "🟡 MAYBE"
        else:
            return "⚠️ RARE"
    
    def generate_deployment_roadmap(self):
        """Show cumulative accuracy improvement as rules are added."""
        
        print("🗺️  Generating deployment roadmap...\n")
        
        # Group by recommendation
        roadmap_data = []
        cumulative_impact = 0
        tier = 1
        
        for idx, row in self.impact_df.iterrows():
            cumulative_impact += float(row['impact_score'])
            
            roadmap_data.append({
                'rank': idx + 1,
                'rule': row['rule'][:60] + '...' if len(row['rule']) > 60 else row['rule'],
                'recommendation': row['recommendation'],
                'impact': row['impact_score'],
                'coverage_%': row['coverage_%'],
                'cumulative_impact': f"{cumulative_impact:.2f}",
                'suggested_tier': self._get_tier(row['recommendation'])
            })
        
        roadmap_df = pd.DataFrame(roadmap_data)
        self.roadmap_df = roadmap_df
        return roadmap_df
    
    def _get_tier(self, recommendation):
        """Assign deployment tier based on recommendation."""
        
        tiers = {
            "🟢 FOUNDATION": "Tier 0: Foundation",
            "⭐ EASY WIN": "Tier 1: Quick Wins",
            "✓ GOOD": "Tier 2: Good Rules",
            "🟡 MAYBE": "Tier 3: Optional",
            "❌ AVOID (negative)": "❌ Skip",
            "⚠️ RARE": "Tier 4: Rare"
        }
        
        return tiers.get(recommendation, "Unknown")
    
    def save_outputs(self):
        """Save all analysis to files."""
        
        print("\n💾 Saving analysis files...\n")
        
        # 1. Rules ranked by impact
        self.impact_df.to_csv(self.output_dir / 'rules_ranked_by_impact.csv', index=False)
        print("  ✓ rules_ranked_by_impact.csv")
        
        # 2. Deployment roadmap
        self.roadmap_df.to_csv(self.output_dir / 'deployment_roadmap.csv', index=False)
        print("  ✓ deployment_roadmap.csv")
        
        # 3. All extracted rules
        rules_df = pd.DataFrame(self.all_rules)
        rules_df.to_csv(self.output_dir / 'rules_all_extracted.csv', index=False)
        print("  ✓ rules_all_extracted.csv")
        
        # 4. Human-readable report
        self.generate_report()
        print("  ✓ rule_impact_report.md")
        
        print(f"\n📂 All files saved to: {self.output_dir}\n")
    
    def generate_report(self):
        """Generate comprehensive markdown report highlighting nested rules."""
        
        report = f"""# Rule Impact Analysis Report

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Dataset:** {self.dataset_path}  
**Total Rules Extracted:** {len(self.rule_occurrences)}  
**Total Rule Occurrences:** {len(self.all_rules)}

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
"""
        
        for idx, (i, row) in enumerate(self.impact_df.head(10).iterrows(), 1):
            rule_short = row['rule'][:55] + '...' if len(row['rule']) > 55 else row['rule']
            report += f"| {idx} | `{rule_short}` | {row['specificity']} | {row['coverage_%']} | {row['impact_score']} | {row['recommendation']} |\n"
        
        report += """

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

"""
        
        broad_rules = self.impact_df[self.impact_df['conditions'] == 1]
        for idx, row in broad_rules.head(5).iterrows():
            report += f"""
**Rule:** `{row['rule']}`
- Coverage: {row['coverage_%']}
- Average Win: {row['avg_win']}
- Impact Score: {row['impact_score']}
- **Action:** Deploy immediately, no question

"""
        
        report += """
### Tier 1: Easy Wins (NESTED Rules - 2-3 Conditions)

These add specificity and often higher accuracy.

"""
        
        nested_rules = self.impact_df[
            (self.impact_df['conditions'] >= 2) & (self.impact_df['conditions'] <= 3) &
            (self.impact_df['recommendation'].isin(['⭐ EASY WIN', '✓ GOOD']))
        ]
        for idx, row in nested_rules.head(5).iterrows():
            report += f"""
**Rule:** `{row['rule']}`
- Conditions: {row['conditions']}
- Coverage: {row['coverage_%']}
- Average Win: {row['avg_win']}
- Impact Score: {row['impact_score']}
- **Action:** Add after foundation for higher accuracy

"""
        
        report += """
### Tier 2: Refinements (DEEPLY NESTED Rules - 4+ Conditions)

High accuracy but narrow scope. Watch diminishing returns.

"""
        
        deep_rules = self.impact_df[self.impact_df['conditions'] >= 4]
        for idx, row in deep_rules.head(3).iterrows():
            report += f"- `{row['rule'][:70]}...` (Impact: {row['impact_score']}, Coverage: {row['coverage_%']})\n"
        
        report += """

### Rules to Skip

Avoid rules with negative impact regardless of nesting depth.

"""
        
        avoid = self.impact_df[self.impact_df['recommendation'] == '❌ AVOID (negative)']
        for idx, row in avoid.head(5).iterrows():
            report += f"- `{row['rule'][:70]}...` (Avg Win: {row['avg_win']}) ❌\n"
        
        report += """

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

"""
        
        with open(self.output_dir / 'rule_impact_report.md', 'w') as f:
            f.write(report)

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Extract and analyze rules from EZR trees')
    parser.add_argument('--runs', type=int, default=50, help='Number of EZR runs')
    parser.add_argument('--dataset', type=str, required=True, help='Path to dataset CSV')
    parser.add_argument('--output-dir', type=str, default='rule_analysis', help='Output directory')
    
    args = parser.parse_args()
    
    # Run analysis
    analyzer = RuleExtractor(args.dataset, args.output_dir)
    analyzer.run_and_extract(args.runs)
    analyzer.calculate_impact_scores()
    analyzer.generate_deployment_roadmap()
    analyzer.save_outputs()
    
    print("✨ Rule impact analysis complete!")
    print(f"📖 Start with: {analyzer.output_dir}/rule_impact_report.md")

if __name__ == '__main__':
    main()
