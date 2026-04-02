#!/usr/bin/env python3
"""
SE4AI: EZR Stability Analysis Script
Runs EZR X times, checks for convergence, analyzes feature frequency and Pareto front.

Usage:
    python3 analyze_ezr_stability.py --runs 20 --dataset BankChurners --stability-check 5
    
Output:
    - all_trees.csv: Complete list of all generated trees
    - feature_frequency.csv: How often each feature appears
    - pareto_front.csv: Trees on the Pareto frontier
    - stability_analysis.csv: Convergence tracking by batch
    - summary_report.md: Human-readable summary
    - results.json: All data in JSON format
"""

import subprocess
import re
import pandas as pd
import json
from pathlib import Path
from collections import defaultdict
import argparse
from datetime import datetime
import sys

class EZRAnalyzer:
    def __init__(self, dataset_path, output_dir="ezr_analysis"):
        self.dataset_path = dataset_path
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Storage for all runs
        self.all_trees = []
        self.feature_frequency = defaultdict(int)
        self.total_runs = 0
        self.stability_history = []
        
    def run_ezr(self, n_runs=20, stability_check_interval=5):
        """Run EZR n_runs times and track stability every stability_check_interval runs."""
        
        print(f"🚀 Starting EZR analysis: {n_runs} runs with stability check every {stability_check_interval} runs")
        print(f"📊 Dataset: {self.dataset_path}")
        print(f"💾 Output directory: {self.output_dir}\n")
        
        for run_num in range(1, n_runs + 1):
            print(f"[Run {run_num}/{n_runs}] Running EZR...")
            
            try:
                # Run EZR command
                result = subprocess.run(
                    ["ezr", "-f", str(self.dataset_path)],
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                
                if result.returncode != 0:
                    print(f"  ⚠️  EZR failed: {result.stderr}")
                    continue
                
                # Parse output
                tree_data = self.parse_ezr_output(result.stdout, run_num)
                if tree_data:
                    self.all_trees.append(tree_data)
                    self.total_runs += 1
                    
                    # Update feature frequency
                    for feature in tree_data['features']:
                        self.feature_frequency[feature] += 1
                    
                    print(f"  ✓ Features: {', '.join(tree_data['features'])}")
                    print(f"  ✓ Accuracy (win): {tree_data['win']}")
                    print(f"  ✓ Complexity: {tree_data['complexity']}")
                
                # Check stability at intervals
                if run_num % stability_check_interval == 0:
                    print(f"\n📈 Stability check at run {run_num}...")
                    stability = self.check_stability(run_num)
                    self.stability_history.append(stability)
                    self.print_stability_report(stability)
                    print()
                    
            except subprocess.TimeoutExpired:
                print(f"  ⚠️  Run {run_num} timed out")
                continue
            except Exception as e:
                print(f"  ⚠️  Error in run {run_num}: {e}")
                continue
        
        print(f"\n✅ Completed {self.total_runs} successful runs")
        
    def parse_ezr_output(self, output, run_num):
        """Parse EZR output to extract tree information."""
        
        # Extract the tree metrics line (last line with #rows, win, features)
        # Format: "19 3 income_Category, card_Category, Contacts_Count_12_mon"
        # or: "73 68" (where 73 is num features evaluated, 68 is win score)
        
        lines = output.strip().split('\n')
        
        # Look for the summary line (has the features and win score)
        tree_info = {
            'run_num': run_num,
            'features': [],
            'win': None,
            'complexity': 0,
            'raw_output': output
        }
        
        # Parse the output to find features and win score
        # The format from your example:
        # 19 3 income_Category, card_Category, Contacts_Count_12_mon
        # 73 68
        # Last two lines are: feature_count, feature_count_in_tree
        #                     rows, win_score
        
        for line in reversed(lines):
            parts = line.strip().split()
            if len(parts) >= 2:
                try:
                    # Try to parse as numbers
                    num1 = int(parts[0])
                    num2 = int(parts[1])
                    
                    # If we have features, this might be the win line
                    if tree_info['features']:
                        tree_info['win'] = num2
                        break
                    
                    # Otherwise, check if there are feature names after the numbers
                    if len(parts) > 2:
                        # This line has features: "19 3 feature1, feature2, ..."
                        features_part = ' '.join(parts[2:])
                        features = [f.strip().rstrip(',') for f in features_part.split(',')]
                        tree_info['features'] = [f for f in features if f]
                        tree_info['complexity'] = len(tree_info['features'])
                except ValueError:
                    # Not numbers, skip
                    continue
        
        # If win not found, try to extract it differently
        if tree_info['win'] is None:
            for line in reversed(lines):
                parts = line.split()
                if len(parts) >= 2:
                    try:
                        last_two = [int(parts[-2]), int(parts[-1])]
                        tree_info['win'] = last_two[1]
                        break
                    except ValueError:
                        continue
        
        # If still no features, try to extract from the detailed output
        if not tree_info['features']:
            for line in lines:
                # Look for "if feature_name ==" pattern
                if " if " in line and " == " in line:
                    match = re.search(r'if\s+(\w+)\s+==', line)
                    if match:
                        feature = match.group(1)
                        if feature not in tree_info['features']:
                            tree_info['features'].append(feature)
            tree_info['complexity'] = len(tree_info['features'])
        
        return tree_info if tree_info['win'] is not None else None
    
    def check_stability(self, run_num):
        """Check if Pareto front and feature frequency have stabilized."""
        
        # Get current Pareto front
        pareto_trees = self.identify_pareto_front()
        
        # Calculate feature frequency percentages
        feature_pcts = {}
        for feature, count in self.feature_frequency.items():
            feature_pcts[feature] = (count / self.total_runs) * 100
        
        # Identify consensus features (>80%)
        consensus_features = {f: pct for f, pct in feature_pcts.items() if pct >= 80}
        
        # Identify exploratory features (<40%)
        exploratory_features = {f: pct for f, pct in feature_pcts.items() if pct < 40}
        
        stability_data = {
            'run_num': run_num,
            'pareto_front_size': len(pareto_trees),
            'num_consensus_features': len(consensus_features),
            'num_exploratory_features': len(exploratory_features),
            'accuracy_range': (
                min(t['win'] for t in pareto_trees) if pareto_trees else None,
                max(t['win'] for t in pareto_trees) if pareto_trees else None
            ),
            'feature_pcts': feature_pcts,
            'consensus_features': consensus_features,
            'exploratory_features': exploratory_features
        }
        
        return stability_data
    
    def identify_pareto_front(self):
        """Identify trees on the Pareto frontier (not dominated on both accuracy AND complexity)."""
        
        frontier = []
        
        for tree in self.all_trees:
            is_dominated = False
            
            for other in self.all_trees:
                # Does 'other' dominate 'tree'?
                # Dominate means: higher/same accuracy AND lower/same complexity
                better_or_equal_accuracy = other['win'] >= tree['win']
                simpler_or_equal = other['complexity'] <= tree['complexity']
                
                if better_or_equal_accuracy and simpler_or_equal:
                    # other is at least as good on both dimensions
                    # Check if it's strictly better on at least one
                    strictly_better_accuracy = other['win'] > tree['win']
                    strictly_simpler = other['complexity'] < tree['complexity']
                    
                    if strictly_better_accuracy or strictly_simpler:
                        is_dominated = True
                        break
            
            if not is_dominated:
                frontier.append(tree)
        
        return frontier
    
    def print_stability_report(self, stability):
        """Print formatted stability report."""
        
        print(f"  Pareto Front Size: {stability['pareto_front_size']}")
        print(f"  Accuracy Range: {stability['accuracy_range']}")
        print(f"  Consensus Features (≥80%): {len(stability['consensus_features'])}")
        
        if stability['consensus_features']:
            for feature, pct in sorted(stability['consensus_features'].items(), 
                                      key=lambda x: x[1], reverse=True):
                print(f"    • {feature}: {pct:.1f}%")
        
        print(f"  Exploratory Features (<40%): {len(stability['exploratory_features'])}")
        if stability['exploratory_features']:
            for feature, pct in sorted(stability['exploratory_features'].items()):
                print(f"    • {feature}: {pct:.1f}%")
    
    def generate_outputs(self):
        """Generate all output files."""
        
        print("\n💾 Generating output files...\n")
        
        # 1. All trees CSV
        self.save_all_trees_csv()
        print("  ✓ all_trees.csv")
        
        # 2. Feature frequency CSV
        self.save_feature_frequency_csv()
        print("  ✓ feature_frequency.csv")
        
        # 3. Pareto front CSV
        self.save_pareto_front_csv()
        print("  ✓ pareto_front.csv")
        
        # 4. Stability analysis CSV
        self.save_stability_analysis_csv()
        print("  ✓ stability_analysis.csv")
        
        # 5. Summary report
        self.save_summary_report()
        print("  ✓ summary_report.md")
        
        # 6. JSON export
        self.save_json_export()
        print("  ✓ results.json")
        
        # 7. Human-readable data export
        self.save_human_readable_export()
        print("  ✓ results_detailed.txt")
        
        # 8. Visualization
        self.save_pareto_visualization()
        print("  ✓ pareto_front.png")
        print("  ✓ pareto_front_detailed.png")
        
        print(f"\n📂 All files saved to: {self.output_dir}\n")
    
    def save_all_trees_csv(self):
        """Save all generated trees to CSV."""
        
        data = []
        for tree in self.all_trees:
            data.append({
                'run_num': tree['run_num'],
                'features': ', '.join(tree['features']),
                'complexity': tree['complexity'],
                'win': tree['win'],
                'on_frontier': self._is_on_frontier(tree)
            })
        
        df = pd.DataFrame(data)
        df.to_csv(self.output_dir / 'all_trees.csv', index=False)
    
    def save_feature_frequency_csv(self):
        """Save feature frequency analysis."""
        
        data = []
        for feature, count in sorted(self.feature_frequency.items(), key=lambda x: x[1], reverse=True):
            pct = (count / self.total_runs) * 100
            
            # Classify feature
            if pct >= 80:
                classification = 'CONSENSUS'
            elif pct >= 60:
                classification = 'IMPORTANT'
            elif pct >= 40:
                classification = 'UNCERTAIN'
            else:
                classification = 'EXPLORATORY'
            
            data.append({
                'feature': feature,
                'count': count,
                'runs': self.total_runs,
                'frequency_%': f'{pct:.1f}%',
                'classification': classification
            })
        
        df = pd.DataFrame(data)
        df.to_csv(self.output_dir / 'feature_frequency.csv', index=False)
    
    def save_pareto_front_csv(self):
        """Save Pareto frontier trees."""
        
        frontier = self.identify_pareto_front()
        
        data = []
        for tree in sorted(frontier, key=lambda x: x['win'], reverse=True):
            data.append({
                'run_num': tree['run_num'],
                'features': ', '.join(tree['features']),
                'complexity': tree['complexity'],
                'win': tree['win'],
                'on_knee': self._is_on_knee(frontier, tree)
            })
        
        df = pd.DataFrame(data)
        df.to_csv(self.output_dir / 'pareto_front.csv', index=False)
    
    def save_stability_analysis_csv(self):
        """Save stability analysis by batch."""
        
        data = []
        for stability in self.stability_history:
            data.append({
                'run_num': stability['run_num'],
                'pareto_front_size': stability['pareto_front_size'],
                'num_consensus_features': stability['num_consensus_features'],
                'num_exploratory_features': stability['num_exploratory_features'],
                'accuracy_min': stability['accuracy_range'][0],
                'accuracy_max': stability['accuracy_range'][1]
            })
        
        df = pd.DataFrame(data)
        df.to_csv(self.output_dir / 'stability_analysis.csv', index=False)
    
    def save_summary_report(self):
        """Save human-readable markdown summary."""
        
        frontier = self.identify_pareto_front()
        
        # Calculate statistics
        feature_pcts = {f: (c / self.total_runs * 100) for f, c in self.feature_frequency.items()}
        consensus = {f: pct for f, pct in feature_pcts.items() if pct >= 80}
        important = {f: pct for f, pct in feature_pcts.items() if 60 <= pct < 80}
        exploratory = {f: pct for f, pct in feature_pcts.items() if pct < 40}
        
        accuracy_values = [t['win'] for t in self.all_trees]
        complexity_values = [t['complexity'] for t in self.all_trees]
        
        report = f"""# SE4AI EZR Stability Analysis Report

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Dataset:** {self.dataset_path}  
**Total Runs:** {self.total_runs}

---

## Executive Summary

After {self.total_runs} EZR runs, the optimization landscape shows:

- **Pareto Front Size:** {len(frontier)} models
- **Consensus Features:** {len(consensus)} (appearing in ≥80% of runs)
- **Exploratory Features:** {len(exploratory)} (appearing in <40% of runs)
- **Accuracy Range:** {min(accuracy_values)} to {max(accuracy_values)}
- **Complexity Range:** {min(complexity_values)} to {max(complexity_values)} features

---

## Consensus Features (≥80% of runs)

Features that appear reliably across the optimization landscape:

"""
        
        if consensus:
            for feature, pct in sorted(consensus.items(), key=lambda x: x[1], reverse=True):
                report += f"- **{feature}**: {pct:.1f}% ({int(pct/100 * self.total_runs)}/{self.total_runs} runs)\n"
        else:
            report += "No consensus features at ≥80% threshold.\n"
        
        report += f"""
---

## Important Features (60-80% of runs)

Features that appear frequently but not consistently:

"""
        
        if important:
            for feature, pct in sorted(important.items(), key=lambda x: x[1], reverse=True):
                report += f"- **{feature}**: {pct:.1f}% ({int(pct/100 * self.total_runs)}/{self.total_runs} runs)\n"
        else:
            report += "No important features in 60-80% range.\n"
        
        report += f"""
---

## Exploratory Features (<40% of runs)

Features that appear rarely and may be dataset-specific artifacts:

"""
        
        if exploratory:
            for feature, pct in sorted(exploratory.items()):
                report += f"- **{feature}**: {pct:.1f}% ({int(pct/100 * self.total_runs)}/{self.total_runs} runs)\n"
        else:
            report += "No exploratory features below 40%.\n"
        
        report += f"""
---

## Pareto Front Analysis

### Frontier Trees (Not dominated on both accuracy AND complexity)

"""
        
        for i, tree in enumerate(sorted(frontier, key=lambda x: x['win'], reverse=True), 1):
            report += f"{i}. **Run {tree['run_num']}**: {tree['complexity']} features, {tree['win']} accuracy\n"
            report += f"   - Features: {', '.join(tree['features'])}\n\n"
        
        report += """
### Interpretation

"""
        
        # Find knee of curve
        min_complexity = min(t['complexity'] for t in frontier)
        knee_candidates = [t for t in frontier if t['complexity'] == min_complexity]
        knee_tree = max(knee_candidates, key=lambda x: x['win'])
        
        report += f"""
The **knee of the curve** (best trade-off) is at Tree {knee_tree['run_num']}:
- Features: {', '.join(knee_tree['features'])}
- Accuracy: {knee_tree['win']}
- Complexity: {knee_tree['complexity']}

Trees with more features show **diminishing returns** on accuracy.

---

## Stability Analysis

Based on stability checks every 5 runs:

"""
        
        for i, stability in enumerate(self.stability_history):
            report += f"**Run {stability['run_num']}:**\n"
            report += f"- Pareto front size: {stability['pareto_front_size']}\n"
            report += f"- Consensus features: {stability['num_consensus_features']}\n"
            report += f"- Exploratory features: {stability['num_exploratory_features']}\n\n"
        
        report += """
### Convergence Assessment

"""
        
        if len(self.stability_history) >= 2:
            sizes = [s['pareto_front_size'] for s in self.stability_history]
            consensus_counts = [s['num_consensus_features'] for s in self.stability_history]
            
            if sizes[-1] == sizes[-2]:
                report += "✅ **Pareto front has stabilized** (size unchanged in last check)\n"
            else:
                report += "⚠️  **Pareto front still changing** (consider more runs)\n"
            
            if consensus_counts[-1] == consensus_counts[-2]:
                report += "✅ **Consensus features have stabilized**\n"
            else:
                report += "⚠️  **Consensus features still changing**\n"
        
        report += f"""

---

## Recommendations

1. **Feature Selection**: Use consensus features (≥80%) for production models
2. **Model Complexity**: Optimal models use {min(t['complexity'] for t in frontier)}-{max(t['complexity'] for t in frontier)} features
3. **Data Requirements**: Focus data quality efforts on consensus features
4. **Further Analysis**: """
        
        if len(self.stability_history) < 2:
            report += "Run more iterations to assess stability"
        elif sizes[-1] != sizes[-2]:
            report += "Run more iterations until Pareto front stabilizes"
        else:
            report += "Pareto front is stable; analysis is complete"
        
        report += f"""

---

## Data Files

- `all_trees.csv`: Complete list of all {self.total_runs} generated trees
- `feature_frequency.csv`: Feature frequency analysis with classifications
- `pareto_front.csv`: Trees on the Pareto frontier
- `stability_analysis.csv`: Stability metrics by run batch
- `results.json`: All data in JSON format for programmatic access

"""
        
        with open(self.output_dir / 'summary_report.md', 'w') as f:
            f.write(report)
    
    def save_json_export(self):
        """Save all results as JSON for programmatic access."""
        
        frontier = self.identify_pareto_front()
        feature_pcts = {f: (c / self.total_runs * 100) for f, c in self.feature_frequency.items()}
        
        data = {
            'metadata': {
                'generated': datetime.now().isoformat(),
                'dataset': str(self.dataset_path),
                'total_runs': self.total_runs
            },
            'all_trees': self.all_trees,
            'feature_frequency': {
                'features': dict(self.feature_frequency),
                'percentages': feature_pcts,
                'consensus': {f: pct for f, pct in feature_pcts.items() if pct >= 80},
                'important': {f: pct for f, pct in feature_pcts.items() if 60 <= pct < 80},
                'exploratory': {f: pct for f, pct in feature_pcts.items() if pct < 40}
            },
            'pareto_front': frontier,
            'stability_history': self.stability_history
        }
        
        with open(self.output_dir / 'results.json', 'w') as f:
            json.dump(data, f, indent=2)
    
    def save_human_readable_export(self):
        """Save all results in human-readable text format."""
        
        frontier = self.identify_pareto_front()
        feature_pcts = {f: (c / self.total_runs * 100) for f, c in self.feature_frequency.items()}
        
        report = f"""================================================================================
EZR STABILITY ANALYSIS - DETAILED RESULTS
================================================================================

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Dataset: {self.dataset_path}
Total Runs: {self.total_runs}

================================================================================
1. ALL GENERATED TREES ({len(self.all_trees)} trees)
================================================================================

"""
        
        for i, tree in enumerate(self.all_trees, 1):
            on_frontier = "✓ ON FRONTIER" if self._is_on_frontier(tree) else "  off frontier"
            report += f"""
Run {tree['run_num']}: {on_frontier}
  Features ({tree['complexity']}): {', '.join(tree['features'])}
  Accuracy (win): {tree['win']}
"""
        
        # Feature frequency section
        report += f"""

================================================================================
2. FEATURE FREQUENCY ANALYSIS
================================================================================

Total Runs: {self.total_runs}

---
CONSENSUS FEATURES (≥80% of runs)
---
"""
        
        consensus = {f: pct for f, pct in feature_pcts.items() if pct >= 80}
        if consensus:
            for feature, pct in sorted(consensus.items(), key=lambda x: x[1], reverse=True):
                count = int(pct / 100 * self.total_runs)
                report += f"  {feature:40s} {count:2d}/{self.total_runs}  {pct:6.1f}%\n"
        else:
            report += "  (None)\n"
        
        report += f"""
---
IMPORTANT FEATURES (60-80% of runs)
---
"""
        
        important = {f: pct for f, pct in feature_pcts.items() if 60 <= pct < 80}
        if important:
            for feature, pct in sorted(important.items(), key=lambda x: x[1], reverse=True):
                count = int(pct / 100 * self.total_runs)
                report += f"  {feature:40s} {count:2d}/{self.total_runs}  {pct:6.1f}%\n"
        else:
            report += "  (None)\n"
        
        report += f"""
---
UNCERTAIN FEATURES (40-60% of runs)
---
"""
        
        uncertain = {f: pct for f, pct in feature_pcts.items() if 40 <= pct < 60}
        if uncertain:
            for feature, pct in sorted(uncertain.items(), key=lambda x: x[1], reverse=True):
                count = int(pct / 100 * self.total_runs)
                report += f"  {feature:40s} {count:2d}/{self.total_runs}  {pct:6.1f}%\n"
        else:
            report += "  (None)\n"
        
        report += f"""
---
EXPLORATORY FEATURES (<40% of runs)
---
"""
        
        exploratory = {f: pct for f, pct in feature_pcts.items() if pct < 40}
        if exploratory:
            for feature, pct in sorted(exploratory.items()):
                count = int(pct / 100 * self.total_runs)
                report += f"  {feature:40s} {count:2d}/{self.total_runs}  {pct:6.1f}%\n"
        else:
            report += "  (None)\n"
        
        # Pareto front section
        report += f"""

================================================================================
3. PARETO FRONT ({len(frontier)} trees on frontier)
================================================================================

Trees that are not dominated on both accuracy AND complexity:

"""
        
        for i, tree in enumerate(sorted(frontier, key=lambda x: x['win'], reverse=True), 1):
            knee_marker = " ← KNEE OF CURVE" if self._is_on_knee(frontier, tree) else ""
            report += f"""
{i}. Run {tree['run_num']}{knee_marker}
   Features ({tree['complexity']}): {', '.join(tree['features'])}
   Accuracy: {tree['win']}
"""
        
        # Stability history section
        report += f"""

================================================================================
4. STABILITY HISTORY (Convergence tracking)
================================================================================

Checked every 5 runs to monitor frontier and feature convergence:

Run #  │ Frontier Size │ Consensus Feat │ Exploratory │ Accuracy Range
─────────────────────────────────────────────────────────────────────────
"""
        
        for stability in self.stability_history:
            run_num = stability['run_num']
            frontier_size = stability['pareto_front_size']
            consensus_count = stability['num_consensus_features']
            exploratory_count = stability['num_exploratory_features']
            acc_min, acc_max = stability['accuracy_range']
            report += f"{run_num:5d}  │      {frontier_size:2d}        │       {consensus_count:2d}        │     {exploratory_count:2d}      │  {acc_min}-{acc_max}\n"
        
        # Summary statistics
        report += f"""

================================================================================
5. SUMMARY STATISTICS
================================================================================

ACCURACY:
  Minimum: {min(t['win'] for t in self.all_trees)}
  Maximum: {max(t['win'] for t in self.all_trees)}
  Mean (frontier): {sum(t['win'] for t in frontier) / len(frontier):.1f}
  Range: {min(t['win'] for t in self.all_trees)} to {max(t['win'] for t in self.all_trees)}

COMPLEXITY (Number of features):
  Minimum: {min(t['complexity'] for t in self.all_trees)}
  Maximum: {max(t['complexity'] for t in self.all_trees)}
  Mean (frontier): {sum(t['complexity'] for t in frontier) / len(frontier):.1f}
  Range: {min(t['complexity'] for t in self.all_trees)} to {max(t['complexity'] for t in self.all_trees)}

FRONTIER CHARACTERISTICS:
  Number of trees: {len(frontier)}
  Minimum complexity: {min(t['complexity'] for t in frontier)}
  Maximum complexity: {max(t['complexity'] for t in frontier)}
  Accuracy range: {min(t['win'] for t in frontier)} to {max(t['win'] for t in frontier)}

FEATURES:
  Total unique features: {len(self.feature_frequency)}
  Consensus (≥80%): {len(consensus)}
  Important (60-80%): {len(important)}
  Uncertain (40-60%): {len(uncertain)}
  Exploratory (<40%): {len(exploratory)}

================================================================================
6. CONVERGENCE ASSESSMENT
================================================================================

"""
        
        if len(self.stability_history) >= 2:
            sizes = [s['pareto_front_size'] for s in self.stability_history]
            consensus_counts = [s['num_consensus_features'] for s in self.stability_history]
            
            report += "PARETO FRONT:\n"
            if sizes[-1] == sizes[-2]:
                report += f"  ✓ STABLE - Frontier size {sizes[-1]} unchanged since run {self.stability_history[-2]['run_num']}\n"
            else:
                report += f"  ⚠ GROWING - Frontier size changed from {sizes[-2]} to {sizes[-1]}\n"
            
            report += "\nCONSENSUS FEATURES:\n"
            if consensus_counts[-1] == consensus_counts[-2]:
                report += f"  ✓ STABLE - {consensus_counts[-1]} consensus features unchanged\n"
            else:
                report += f"  ⚠ CHANGING - Consensus features changed from {consensus_counts[-2]} to {consensus_counts[-1]}\n"
        
        report += """

================================================================================
7. RECOMMENDATIONS
================================================================================

1. FEATURE SELECTION:
   - Use CONSENSUS features (≥80%) in production models
   - Investigate IMPORTANT features (60-80%)
   - Avoid EXPLORATORY features (<40%) unless well-justified

2. MODEL ARCHITECTURE:
   - The knee of the curve (minimum complexity with max accuracy) is at:
"""
        
        if frontier:
            min_complexity = min(t['complexity'] for t in frontier)
            knee_candidates = [t for t in frontier if t['complexity'] == min_complexity]
            knee_tree = max(knee_candidates, key=lambda x: x['win'])
            report += f"     {min_complexity} features with {knee_tree['win']} accuracy\n"
            report += f"   - No significant accuracy gain beyond this point\n"
        
        report += f"""
3. DATA QUALITY:
   - Prioritize consensus features for data collection and validation
   - These appear in 80%+ of optimized models

4. FURTHER ANALYSIS:
"""
        
        if len(self.stability_history) >= 2:
            sizes = [s['pareto_front_size'] for s in self.stability_history]
            if sizes[-1] != sizes[-2]:
                report += "   - Run more iterations (frontier still growing)\n"
            else:
                report += "   - Current analysis is stable and sufficient\n"
        
        report += """
================================================================================

For detailed analysis, see:
  - summary_report.md: Executive summary with interpretation
  - pareto_front.csv: Frontier trees in tabular format
  - feature_frequency.csv: Feature usage with classifications
  - all_trees.csv: Complete tree listing
  - stability_analysis.csv: Convergence metrics by batch

================================================================================
"""
        
        with open(self.output_dir / 'results_detailed.txt', 'w') as f:
            f.write(report)
    
    def _is_on_frontier(self, tree):
        """Check if a tree is on the Pareto frontier."""
        frontier = self.identify_pareto_front()
        return any(t['run_num'] == tree['run_num'] for t in frontier)
    
    def _is_on_knee(self, frontier, tree):
        """Check if a tree is on the knee of the curve."""
        min_complexity = min(t['complexity'] for t in frontier)
        if tree['complexity'] != min_complexity:
            return False
        
        # Among trees with min complexity, is this the one with best accuracy?
        min_complexity_trees = [t for t in frontier if t['complexity'] == min_complexity]
        return tree['win'] == max(t['win'] for t in min_complexity_trees)
    
    def save_pareto_visualization(self):
        """Generate Pareto front visualizations."""
        
        try:
            import matplotlib.pyplot as plt
            import matplotlib.patches as mpatches
        except ImportError:
            print("\n  ⚠️  matplotlib not installed, skipping visualizations")
            print("     Install with: pip install matplotlib")
            return
        
        frontier = self.identify_pareto_front()
        
        # Separate frontier and non-frontier trees
        frontier_trees = frontier
        non_frontier_trees = [t for t in self.all_trees if t not in frontier_trees]
        
        # Find knee
        min_complexity = min(t['complexity'] for t in frontier_trees)
        knee_candidates = [t for t in frontier_trees if t['complexity'] == min_complexity]
        knee_tree = max(knee_candidates, key=lambda x: x['win'])
        
        # ===== FIGURE 1: Simple Pareto Front =====
        fig, ax = plt.subplots(figsize=(10, 7))
        
        # Plot non-frontier trees
        if non_frontier_trees:
            x_nf = [t['complexity'] for t in non_frontier_trees]
            y_nf = [t['win'] for t in non_frontier_trees]
            ax.scatter(x_nf, y_nf, s=100, alpha=0.4, color='#cccccc', 
                      label='Off-frontier', edgecolors='#666666', linewidth=0.5)
        
        # Plot frontier trees
        if frontier_trees:
            x_f = [t['complexity'] for t in frontier_trees]
            y_f = [t['win'] for t in frontier_trees]
            ax.scatter(x_f, y_f, s=150, alpha=0.8, color='#2ecc71', 
                      label='Pareto frontier', edgecolors='#27ae60', linewidth=1.5)
        
        # Highlight knee
        ax.scatter([knee_tree['complexity']], [knee_tree['win']], 
                  s=300, alpha=1.0, color='#e74c3c', marker='*',
                  label='Knee (optimal)', edgecolors='#c0392b', linewidth=2, zorder=5)
        
        # Add connecting line for frontier
        if frontier_trees:
            sorted_frontier = sorted(frontier_trees, key=lambda x: x['complexity'])
            x_line = [t['complexity'] for t in sorted_frontier]
            y_line = [t['win'] for t in sorted_frontier]
            ax.plot(x_line, y_line, 'g--', alpha=0.3, linewidth=1)
        
        ax.set_xlabel('Complexity (Number of Features)', fontsize=12, fontweight='bold')
        ax.set_ylabel('Accuracy (Win Score)', fontsize=12, fontweight='bold')
        ax.set_title('Pareto Front: Accuracy vs. Complexity Trade-off', 
                    fontsize=14, fontweight='bold', pad=20)
        ax.legend(loc='best', fontsize=10)
        ax.grid(True, alpha=0.3)
        ax.set_axisbelow(True)
        
        # Add annotations
        ax.text(0.02, 0.98, f'Total runs: {self.total_runs}\nFrontier size: {len(frontier_trees)}',
               transform=ax.transAxes, fontsize=10, verticalalignment='top',
               bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
        plt.tight_layout()
        plt.savefig(self.output_dir / 'pareto_front.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # ===== FIGURE 2: Detailed Pareto Front with Run Numbers =====
        fig, ax = plt.subplots(figsize=(14, 8))
        
        # Plot non-frontier trees
        if non_frontier_trees:
            x_nf = [t['complexity'] for t in non_frontier_trees]
            y_nf = [t['win'] for t in non_frontier_trees]
            ax.scatter(x_nf, y_nf, s=100, alpha=0.4, color='#cccccc', 
                      label='Off-frontier', edgecolors='#666666', linewidth=0.5)
            
            # Add labels for non-frontier
            for tree in non_frontier_trees:
                ax.annotate(f"R{tree['run_num']}", 
                           xy=(tree['complexity'], tree['win']),
                           xytext=(3, 3), textcoords='offset points',
                           fontsize=8, alpha=0.5)
        
        # Plot frontier trees
        if frontier_trees:
            x_f = [t['complexity'] for t in frontier_trees]
            y_f = [t['win'] for t in frontier_trees]
            ax.scatter(x_f, y_f, s=200, alpha=0.8, color='#2ecc71', 
                      label='Pareto frontier', edgecolors='#27ae60', linewidth=2)
            
            # Add labels for frontier
            for tree in frontier_trees:
                ax.annotate(f"Run {tree['run_num']}", 
                           xy=(tree['complexity'], tree['win']),
                           xytext=(5, 5), textcoords='offset points',
                           fontsize=9, fontweight='bold', color='#27ae60')
        
        # Highlight knee
        ax.scatter([knee_tree['complexity']], [knee_tree['win']], 
                  s=400, alpha=1.0, color='#e74c3c', marker='*',
                  label='Knee (optimal)', edgecolors='#c0392b', linewidth=2, zorder=5)
        
        # Add knee annotation
        ax.annotate(f"KNEE\nRun {knee_tree['run_num']}\n{knee_tree['complexity']} feat\n{knee_tree['win']} acc",
                   xy=(knee_tree['complexity'], knee_tree['win']),
                   xytext=(20, 20), textcoords='offset points',
                   fontsize=10, fontweight='bold',
                   bbox=dict(boxstyle='round,pad=0.5', facecolor='#e74c3c', alpha=0.7, edgecolor='#c0392b', linewidth=2),
                   arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0', color='#c0392b', lw=2))
        
        # Add connecting line for frontier
        if frontier_trees:
            sorted_frontier = sorted(frontier_trees, key=lambda x: x['complexity'])
            x_line = [t['complexity'] for t in sorted_frontier]
            y_line = [t['win'] for t in sorted_frontier]
            ax.plot(x_line, y_line, 'g--', alpha=0.3, linewidth=1.5, label='Frontier path')
        
        ax.set_xlabel('Complexity (Number of Features)', fontsize=13, fontweight='bold')
        ax.set_ylabel('Accuracy (Win Score)', fontsize=13, fontweight='bold')
        ax.set_title('Pareto Front Analysis - Detailed View with Run Numbers', 
                    fontsize=14, fontweight='bold', pad=20)
        ax.legend(loc='best', fontsize=11)
        ax.grid(True, alpha=0.3)
        ax.set_axisbelow(True)
        
        # Add info box
        info_text = f"""Total Runs: {self.total_runs}
Frontier Size: {len(frontier_trees)}
Knee Point: Run {knee_tree['run_num']}
Optimal: {knee_tree['complexity']} features, {knee_tree['win']} accuracy

Frontier Accuracy: {min(t['win'] for t in frontier_trees)}-{max(t['win'] for t in frontier_trees)}
Frontier Complexity: {min(t['complexity'] for t in frontier_trees)}-{max(t['complexity'] for t in frontier_trees)}"""
        
        ax.text(0.02, 0.98, info_text,
               transform=ax.transAxes, fontsize=10, verticalalignment='top',
               bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8, edgecolor='gray', linewidth=1))
        
        plt.tight_layout()
        plt.savefig(self.output_dir / 'pareto_front_detailed.png', dpi=300, bbox_inches='tight')
        plt.close()


def main():
    parser = argparse.ArgumentParser(description='Analyze EZR stability and convergence')
    parser.add_argument('--runs', type=int, default=20, help='Number of EZR runs (default: 20)')
    parser.add_argument('--dataset', type=str, required=True, help='Path to dataset CSV')
    parser.add_argument('--stability-check', type=int, default=5, 
                       help='Check stability every N runs (default: 5)')
    parser.add_argument('--output-dir', type=str, default='ezr_analysis', 
                       help='Output directory (default: ezr_analysis)')
    
    args = parser.parse_args()
    
    # Validate dataset exists
    dataset_path = Path(args.dataset)
    if not dataset_path.exists():
        print(f"❌ Error: Dataset not found: {args.dataset}")
        sys.exit(1)
    
    # Run analysis
    analyzer = EZRAnalyzer(dataset_path, args.output_dir)
    analyzer.run_ezr(args.runs, args.stability_check)
    analyzer.generate_outputs()
    
    print("✨ Analysis complete!")
    print(f"📊 View results in: {analyzer.output_dir}/")
    print(f"📖 Start with: {analyzer.output_dir}/summary_report.md")


if __name__ == '__main__':
    main()
