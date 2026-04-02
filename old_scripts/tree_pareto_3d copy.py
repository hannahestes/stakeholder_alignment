#!/usr/bin/env python3
"""
3D Pareto Analysis for Decision Trees
Analyzes complete trees on: Accuracy × Simplicity × Stability

Dimensions:
- Accuracy: Final win% of tree
- Simplicity: Number of unique features used
- Stability: How many other trees use the same feature set (penetration%)

Usage:
    python3 tree_pareto_3d.py --runs 50 --dataset BankChurners.csv

Outputs:
    - trees_analyzed.csv: All trees with 3D metrics
    - pareto_frontier_3d.csv: Frontier trees only
    - pareto_3d.png: 3D scatter plot
"""

import subprocess
import re
import pandas as pd
from pathlib import Path
from collections import defaultdict
from datetime import datetime
import sys

class Tree3DAnalyzer:
    def __init__(self, dataset_path, output_dir="tree_analysis_3d"):
        self.dataset_path = dataset_path
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        self.trees = []  # List of tree data
        self.feature_set_counts = defaultdict(int)  # Count occurrences of each feature set
        
    def extract_features_from_tree(self, output):
        """Extract all unique features used in a tree from EZR output.
        
        EZR output format has a features line like:
        19 3 income_Category, card_Category, Total_Trans_Ct
        
        This extracts: [income_Category, card_Category, Total_Trans_Ct]
        """
        features = set()
        
        lines = output.strip().split('\n')
        
        # Look for features line (has commas and feature names)
        for line in lines:
            line = line.strip()
            
            # Skip empty lines and headers
            if not line or line.startswith('#') or line.startswith('Used:') or line.startswith('Rank'):
                continue
            
            # Features line has format: "complexity count feature1, feature2, ..."
            # Look for lines with commas (indicating multiple features)
            if ',' in line:
                # Split by spaces
                parts = line.split()
                
                # Find where the feature names start
                # (usually after 2 numeric values at the beginning)
                feature_start_idx = 0
                numeric_count = 0
                
                for i, part in enumerate(parts):
                    try:
                        # Try to parse as number
                        float(part)
                        numeric_count += 1
                        feature_start_idx = i + 1
                    except ValueError:
                        # Not a number, this is where features start
                        break
                
                # Extract the feature part
                if feature_start_idx < len(parts):
                    feature_text = ' '.join(parts[feature_start_idx:])
                    # Split by comma and clean up
                    feature_list = [f.strip() for f in feature_text.split(',')]
                    # Filter out empty strings
                    feature_list = [f for f in feature_list if f]
                    features.update(feature_list)
        
        return sorted(list(features)) if features else []
    
    def extract_tree_metrics(self, output, run_num):
        """Extract accuracy and features from EZR output."""
        
        lines = output.strip().split('\n')
        
        accuracy = None
        features = []
        
        # Get final accuracy (last numeric line)
        for line in reversed(lines):
            parts = line.strip().split()
            if len(parts) >= 1:
                try:
                    # Last line should have: total_evals final_win
                    if len(parts) >= 2:
                        final_win = int(parts[-1])
                        accuracy = final_win
                        break
                except (ValueError, IndexError):
                    continue
        
        # Extract features
        features = self.extract_features_from_tree(output)
        
        return {
            'run': run_num,
            'accuracy': accuracy if accuracy is not None else 0,
            'features': features,
            'num_features': len(features),
            'feature_set': tuple(sorted(features)),  # For grouping
        }
    
    def run_and_analyze(self, n_runs=50):
        """Run EZR multiple times and analyze trees."""
        
        print(f"🚀 Running EZR {n_runs} times...\n")
        
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
                
                # Extract tree metrics
                metrics = self.extract_tree_metrics(result.stdout, run_num)
                self.trees.append(metrics)
                
                # Track feature set occurrences
                self.feature_set_counts[metrics['feature_set']] += 1
                
                if run_num % 10 == 0:
                    print(f"  ✓ Completed {run_num}/{n_runs} runs")
                    
            except Exception as e:
                print(f"⚠️  Error in run {run_num}: {e}")
                continue
        
        print(f"\n✅ Analysis complete: {len(self.trees)} trees analyzed\n")
        
        # Calculate stability (penetration%) for each tree
        for tree in self.trees:
            stability = (self.feature_set_counts[tree['feature_set']] / len(self.trees)) * 100
            tree['stability'] = stability
            tree['feature_set_name'] = ', '.join(tree['feature_set'])
    
    def calculate_3d_pareto(self):
        """Identify trees on 3D Pareto frontier.
        
        A tree is on frontier if no other tree dominates it on all 3 dimensions:
        - Higher accuracy
        - Lower simplicity (fewer features)
        - Higher stability
        """
        
        if not self.trees:
            return []
        
        frontier = []
        
        for tree_a in self.trees:
            is_dominated = False
            
            for tree_b in self.trees:
                if tree_a == tree_b:
                    continue
                
                # tree_b dominates tree_a if:
                # - tree_b has higher or equal accuracy AND
                # - tree_b has fewer or equal features AND
                # - tree_b has higher or equal stability
                # AND at least one is strictly better
                
                better_accuracy = tree_b['accuracy'] > tree_a['accuracy']
                better_simplicity = tree_b['num_features'] < tree_a['num_features']
                better_stability = tree_b['stability'] > tree_a['stability']
                
                same_or_better_accuracy = tree_b['accuracy'] >= tree_a['accuracy']
                same_or_better_simplicity = tree_b['num_features'] <= tree_a['num_features']
                same_or_better_stability = tree_b['stability'] >= tree_a['stability']
                
                # Dominates if better on all three
                if (same_or_better_accuracy and same_or_better_simplicity and same_or_better_stability):
                    if better_accuracy or better_simplicity or better_stability:
                        is_dominated = True
                        break
            
            if not is_dominated:
                frontier.append(tree_a)
        
        return frontier
    
    def find_knee_point(self, trees):
        """Find the knee point in 3D space (best balanced tree).
        
        The knee is the tree that best balances all three objectives:
        - Maximize accuracy
        - Minimize features  
        - Maximize stability
        """
        if not trees:
            return None
        
        # Normalize each dimension to 0-1 scale
        accuracies = [t['accuracy'] for t in trees]
        features = [t['num_features'] for t in trees]
        stabilities = [t['stability'] for t in trees]
        
        min_acc, max_acc = min(accuracies), max(accuracies)
        min_feat, max_feat = min(features), max(features)
        min_stab, max_stab = min(stabilities), max(stabilities)
        
        # Calculate normalized scores (0-1)
        best_knee = None
        best_score = -float('inf')
        
        for tree in trees:
            # Normalize accuracy (higher is better, so 1 - normalize isn't needed)
            norm_acc = (tree['accuracy'] - min_acc) / max(max_acc - min_acc, 1)
            
            # Normalize features (fewer is better, so flip it)
            norm_feat = 1 - ((tree['num_features'] - min_feat) / max(max_feat - min_feat, 1))
            
            # Normalize stability (higher is better)
            norm_stab = (tree['stability'] - min_stab) / max(max_stab - min_stab, 1)
            
            # Composite score: average of normalized dimensions
            # Weight them equally
            score = (norm_acc + norm_feat + norm_stab) / 3
            
            if score > best_score:
                best_score = score
                best_knee = tree
        
        return best_knee
    
    def generate_3d_visualization(self):
        """Create 3D scatter plot of trees."""
        
        try:
            import matplotlib.pyplot as plt
            from mpl_toolkits.mplot3d import Axes3D
        except ImportError:
            print("⚠️  matplotlib not installed, skipping 3D visualization")
            return
        
        # Get frontier and knee
        frontier = self.calculate_3d_pareto()
        knee = self.find_knee_point(self.trees)
        frontier_indices = set(self.trees.index(t) for t in frontier if t in self.trees)
        
        # Create figure
        fig = plt.figure(figsize=(14, 10))
        ax = fig.add_subplot(111, projection='3d')
        
        # Plot off-frontier trees
        off_frontier = [t for i, t in enumerate(self.trees) if i not in frontier_indices]
        if off_frontier:
            ax.scatter(
                [t['num_features'] for t in off_frontier],
                [t['stability'] for t in off_frontier],
                [t['accuracy'] for t in off_frontier],
                c='#cccccc', s=80, alpha=0.4, label='Off-frontier',
                edgecolors='#666666', linewidth=0.5
            )
        
        # Plot frontier trees
        if frontier:
            ax.scatter(
                [t['num_features'] for t in frontier],
                [t['stability'] for t in frontier],
                [t['accuracy'] for t in frontier],
                c='#2ecc71', s=150, alpha=0.8, label='Pareto frontier',
                edgecolors='#27ae60', linewidth=2
            )
            
            # Label frontier points
            for t in frontier:
                ax.text(
                    t['num_features'], t['stability'], t['accuracy'],
                    f"  F:{t['num_features']} S:{t['stability']:.0f}% A:{t['accuracy']:.0f}%",
                    fontsize=9, color='#27ae60'
                )
        
        # Highlight knee point
        if knee:
            ax.scatter(
                [knee['num_features']], [knee['stability']], [knee['accuracy']],
                c='#e74c3c', s=300, marker='*', alpha=1.0, label='Knee (optimal)',
                edgecolors='#c0392b', linewidth=2, zorder=5
            )
            
            # Annotate knee
            knee_text = f"OPTIMAL\n{knee['num_features']} features\n{knee['accuracy']:.0f}% accuracy\n{knee['stability']:.0f}% stable"
            ax.text(
                knee['num_features'] + 0.3, knee['stability'] + 5, knee['accuracy'] + 3,
                knee_text,
                fontsize=10, fontweight='bold', color='#c0392b',
                bbox=dict(boxstyle='round', facecolor='#e74c3c', alpha=0.7, edgecolor='#c0392b')
            )
        
        # Labels and formatting
        ax.set_xlabel('Simplicity (# Features)', fontsize=12, fontweight='bold')
        ax.set_ylabel('Stability (% same features)', fontsize=12, fontweight='bold')
        ax.set_zlabel('Accuracy (%)', fontsize=12, fontweight='bold')
        ax.set_title('3D Pareto Front: Accuracy × Simplicity × Stability', 
                    fontsize=14, fontweight='bold', pad=20)
        
        ax.legend(loc='upper left', fontsize=11)
        
        # Add grid
        ax.grid(True, alpha=0.3)
        
        # Info box
        info_text = f"""Trees: {len(self.trees)}
Frontier Size: {len(frontier)}
Feature Range: {min(t['num_features'] for t in self.trees)}-{max(t['num_features'] for t in self.trees)}
Accuracy Range: {min(t['accuracy'] for t in self.trees):.0f}%-{max(t['accuracy'] for t in self.trees):.0f}%
Stability Range: {min(t['stability'] for t in self.trees):.0f}%-{max(t['stability'] for t in self.trees):.0f}%

Knee Point (Optimal):
  Accuracy: {knee['accuracy']:.0f}%
  Features: {knee['num_features']}
  Stability: {knee['stability']:.0f}%"""
        
        ax.text2D(0.02, 0.98, info_text, transform=ax.transAxes,
                 fontsize=10, verticalalignment='top',
                 bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))
        
        plt.tight_layout()
        plt.savefig(self.output_dir / 'pareto_3d.png', dpi=300, bbox_inches='tight')
        print("  ✓ pareto_3d.png")
        plt.close()
    
    def save_outputs(self):
        """Save analysis to CSV files."""
        
        print("\n💾 Saving outputs...\n")
        
        # All trees
        trees_df = pd.DataFrame(self.trees)
        trees_df.to_csv(self.output_dir / 'trees_analyzed.csv', index=False)
        print("  ✓ trees_analyzed.csv")
        
        # Frontier only
        frontier = self.calculate_3d_pareto()
        frontier_df = pd.DataFrame(frontier)
        frontier_df.to_csv(self.output_dir / 'pareto_frontier_3d.csv', index=False)
        print("  ✓ pareto_frontier_3d.csv")
        
        # Feature set summary
        feature_summary = []
        for feature_set, count in self.feature_set_counts.items():
            stability = (count / len(self.trees)) * 100
            feature_summary.append({
                'features': ', '.join(feature_set),
                'num_features': len(feature_set),
                'occurrences': count,
                'stability_%': stability,
            })
        
        feature_summary_df = pd.DataFrame(feature_summary).sort_values('stability_%', ascending=False)
        feature_summary_df.to_csv(self.output_dir / 'feature_sets_summary.csv', index=False)
        print("  ✓ feature_sets_summary.csv")
        
        # 3D visualization
        self.generate_3d_visualization()
        
        print(f"\n📂 All files saved to: {self.output_dir}\n")
    
    def print_summary(self):
        """Print analysis summary."""
        
        if not self.trees:
            print("❌ No trees analyzed!")
            return
        
        frontier = self.calculate_3d_pareto()
        
        print("\n" + "="*80)
        print("3D PARETO ANALYSIS SUMMARY")
        print("="*80)
        print(f"\nTotal Trees: {len(self.trees)}")
        print(f"Frontier Size: {len(frontier)}")
        print(f"\nAccuracy Range: {min(t['accuracy'] for t in self.trees):.0f}% - {max(t['accuracy'] for t in self.trees):.0f}%")
        print(f"Simplicity Range: {min(t['num_features'] for t in self.trees)} - {max(t['num_features'] for t in self.trees)} features")
        print(f"Stability Range: {min(t['stability'] for t in self.trees):.0f}% - {max(t['stability'] for t in self.trees):.0f}%")
        
        print("\n" + "-"*80)
        print("TOP FRONTIER TREES")
        print("-"*80)
        
        frontier_sorted = sorted(frontier, key=lambda x: x['accuracy'], reverse=True)
        for i, tree in enumerate(frontier_sorted[:5], 1):
            print(f"\n{i}. Run {tree['run']}")
            print(f"   Accuracy: {tree['accuracy']:.0f}%")
            print(f"   Features: {tree['num_features']} ({tree['feature_set_name']})")
            print(f"   Stability: {tree['stability']:.0f}% (appeared in {int(tree['stability']*len(self.trees)/100)}/50 runs)")
        
        print("\n" + "="*80 + "\n")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='3D Pareto analysis of decision trees')
    parser.add_argument('--runs', type=int, default=50, help='Number of EZR runs')
    parser.add_argument('--dataset', type=str, required=True, help='Path to dataset')
    
    args = parser.parse_args()
    
    analyzer = Tree3DAnalyzer(args.dataset)
    analyzer.run_and_analyze(args.runs)
    analyzer.save_outputs()
    analyzer.print_summary()


if __name__ == '__main__':
    main()
