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
