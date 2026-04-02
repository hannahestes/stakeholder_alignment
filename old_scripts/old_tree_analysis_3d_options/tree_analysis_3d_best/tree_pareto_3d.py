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
        self.feature_frequency = {}  # Track frequency of each feature across all runs
        
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
        
        # First pass: extract all trees and track feature frequency
        feature_frequency = defaultdict(int)
        
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
                
                # Track individual feature frequencies
                for feature in metrics['features']:
                    feature_frequency[feature] += 1
                
                if run_num % 10 == 0:
                    print(f"  ✓ Completed {run_num}/{n_runs} runs")
                    
            except Exception as e:
                print(f"⚠️  Error in run {run_num}: {e}")
                continue
        
        print(f"\n✅ Analysis complete: {len(self.trees)} trees analyzed\n")
        
        # Calculate stability based on feature frequency
        # Stability = average frequency of the features used in this tree
        for tree in self.trees:
            if len(tree['features']) > 0:
                feature_freqs = [feature_frequency[f] for f in tree['features']]
                avg_freq = sum(feature_freqs) / len(feature_freqs)
                stability = (avg_freq / len(self.trees)) * 100
            else:
                stability = 0
            
            tree['stability'] = stability
            tree['feature_set_name'] = ', '.join(tree['features']) if tree['features'] else '(no features)'
        
        # Store feature frequency for reporting
        self.feature_frequency = feature_frequency
    
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
        """Create publication-quality 3D Pareto visualization."""
        
        try:
            import matplotlib.pyplot as plt
            from mpl_toolkits.mplot3d import Axes3D
            import numpy as np
            from matplotlib.colors import Normalize
        except ImportError:
            print("⚠️  matplotlib not installed, skipping 3D visualization")
            return
        
        # Get frontier and knee
        frontier = self.calculate_3d_pareto()
        knee = self.find_knee_point(self.trees)
        frontier_indices = set(self.trees.index(t) for t in frontier if t in self.trees)
        
        # Create figure with better size and DPI
        fig = plt.figure(figsize=(16, 12), dpi=100)
        ax = fig.add_subplot(111, projection='3d')
        
        # Extract coordinates
        feat_array = np.array([t['num_features'] for t in self.trees])
        stab_array = np.array([t['stability'] for t in self.trees])
        acc_array = np.array([t['accuracy'] for t in self.trees])
        
        # Plot off-frontier trees (subtle)
        off_frontier = [t for i, t in enumerate(self.trees) if i not in frontier_indices]
        if off_frontier:
            ax.scatter(
                [t['num_features'] for t in off_frontier],
                [t['stability'] for t in off_frontier],
                [t['accuracy'] for t in off_frontier],
                c='#e0e0e0', s=60, alpha=0.3, label='Off-frontier trees',
                edgecolors='#999999', linewidth=0.3
            )
        
        # Create colored frontier surface
        if len(frontier) >= 3:
            # Extract frontier coordinates
            feat_frontier = np.array([t['num_features'] for t in frontier])
            stab_frontier = np.array([t['stability'] for t in frontier])
            acc_frontier = np.array([t['accuracy'] for t in frontier])
            
            # Create triangulated surface colored by accuracy
            norm = Normalize(vmin=acc_frontier.min(), vmax=acc_frontier.max())
            
            # Plot surface with RdYlGn colormap (red=high accuracy, green=low)
            surf = ax.plot_trisurf(
                feat_frontier, stab_frontier, acc_frontier,
                cmap='RdYlGn', norm=norm, alpha=0.75,
                edgecolor='#444444', linewidth=0.5, shade=True, antialiased=True
            )
            
            # Add colorbar for accuracy
            cbar = plt.colorbar(surf, ax=ax, pad=0.1, shrink=0.8)
            cbar.set_label('Accuracy (%)', fontsize=12, fontweight='bold')
        
        # Plot frontier points with better styling
        if frontier:
            frontier_acc = np.array([t['accuracy'] for t in frontier])
            scatter = ax.scatter(
                [t['num_features'] for t in frontier],
                [t['stability'] for t in frontier],
                [t['accuracy'] for t in frontier],
                c=frontier_acc, cmap='RdYlGn', s=200, alpha=0.95,
                edgecolors='#1a1a1a', linewidth=2, zorder=5, norm=norm
            )
        
        # Label only top 3-5 frontier points (by accuracy) - just numbers
        frontier_sorted = sorted(frontier, key=lambda x: x['accuracy'], reverse=True)[:5]
        for i, tree in enumerate(frontier_sorted, 1):
            # Just label with number
            label_text = str(i)
            
            # Offset labels to avoid overlap
            x_offset = tree['num_features'] + (0.2 if i % 2 == 0 else -0.2)
            y_offset = tree['stability'] + (3 if i % 2 == 0 else -3)
            z_offset = tree['accuracy'] + 5
            
            # Position labels with better spacing
            ax.text(
                x_offset, y_offset, z_offset,
                label_text,
                fontsize=12, fontweight='bold', color='#1a1a1a',
                bbox=dict(boxstyle='circle,pad=0.4', facecolor='white', alpha=0.95, 
                         edgecolor='#1a1a1a', linewidth=2),
                ha='center', va='center'
            )
        
        # Highlight knee point with large star
        if knee:
            ax.scatter(
                [knee['num_features']], [knee['stability']], [knee['accuracy']],
                c='#e74c3c', s=800, marker='*', alpha=1.0, 
                edgecolors='#c0392b', linewidth=2.5, zorder=10, label='Knee (optimal)'
            )
            
            # Knee annotation box
            knee_text = f"OPTIMAL BALANCE\n{knee['num_features']} features\n{knee['accuracy']:.0f}% accuracy\n{knee['stability']:.0f}% stable"
            ax.text(
                knee['num_features'] + 0.5, knee['stability'] + 6, knee['accuracy'] + 8,
                knee_text,
                fontsize=11, fontweight='bold', color='white',
                bbox=dict(boxstyle='round,pad=0.8', facecolor='#e74c3c', alpha=0.95, 
                         edgecolor='#c0392b', linewidth=2.5)
            )
        
        # Add zone backgrounds (safe/balanced/risky)
        # Safe zone: low features, high stability
        ax.text(2, 75, 10, 'SAFE ZONE\n(Simple & Stable)', 
               fontsize=11, fontweight='bold', color='#27ae60', alpha=0.7,
               bbox=dict(boxstyle='round', facecolor='#d5f4e6', alpha=0.3, edgecolor='#27ae60', linewidth=1))
        
        # Risky zone: high features, low stability
        ax.text(6, 35, 15, 'RISKY ZONE\n(Complex & Unstable)',
               fontsize=11, fontweight='bold', color='#e74c3c', alpha=0.7,
               bbox=dict(boxstyle='round', facecolor='#fadbd8', alpha=0.3, edgecolor='#e74c3c', linewidth=1))
        
        # Consolidated legend box
        legend_text = """VISUALIZATION KEY
━━━━━━━━━━━━━━━━━━━━━━━━━
COLORS (Surface & Points):
  🟥 Red = High Accuracy
  🟨 Yellow = Medium Accuracy
  🟩 Green = Low Accuracy
  ⚪ Light Gray = Off-frontier trees

SYMBOLS:
  ⭐ Red Star = Knee (optimal balance)
  • Black Circles = Frontier trees"""
        
        fig.text(0.98, 0.02, legend_text, transform=fig.transFigure,
                fontsize=9, family='monospace', verticalalignment='bottom', horizontalalignment='right',
                bbox=dict(boxstyle='round', facecolor='#f0f0f0', alpha=0.95, 
                         edgecolor='#333333', linewidth=1.5))
        
        # Axes labels with better formatting
        ax.set_xlabel('\nSimplicity (# Features)', fontsize=13, fontweight='bold', labelpad=10)
        ax.set_ylabel('\nStability (% Feature Frequency)', fontsize=13, fontweight='bold', labelpad=10)
        ax.set_zlabel('\nAccuracy (%)', fontsize=13, fontweight='bold', labelpad=10)
        
        # Title
        ax.set_title('3D Pareto Front: Accuracy × Simplicity × Stability\n(Feature Frequency-Based Stability)', 
                    fontsize=16, fontweight='bold', pad=30)
        
        # Legend
        ax.legend(loc='upper left', fontsize=11, framealpha=0.95, edgecolor='black')
        
        # Optimize viewing angle (rotate to show frontier prominently)
        ax.view_init(elev=25, azim=45)
        
        # Grid
        ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.5)
        ax.xaxis.pane.fill = False
        ax.yaxis.pane.fill = False
        ax.zaxis.pane.fill = False
        
        # Frontier points table
        table_text = "FRONTIER POINTS REFERENCE\n"
        table_text += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        table_text += " #  Acc    Sim  Stab    Run\n"
        table_text += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        
        frontier_sorted = sorted(frontier, key=lambda x: x['accuracy'], reverse=True)[:5]
        for i, tree in enumerate(frontier_sorted, 1):
            table_text += f" {i}  {tree['accuracy']:3.0f}%  {tree['num_features']}    {tree['stability']:2.0f}%   Run {tree['run']}\n"
        
        fig.text(0.02, 0.98, table_text, transform=fig.transFigure,
                fontsize=9, verticalalignment='top', family='monospace',
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.95, 
                         edgecolor='#333333', linewidth=1.5))
        
        # Summary info box (smaller)
        info_text = f"""SUMMARY
Trees: {len(self.trees)} | Frontier: {len(frontier)}
Acc: {min(t['accuracy'] for t in self.trees):.0f}%-{max(t['accuracy'] for t in self.trees):.0f}%
Sim: {min(f['num_features'] for f in self.trees)}-{max(f['num_features'] for f in self.trees)}
Stab: {min(t['stability'] for t in self.trees):.0f}%-{max(t['stability'] for t in self.trees):.0f}%"""
        
        fig.text(0.02, 0.65, info_text, transform=fig.transFigure,
                fontsize=9, verticalalignment='top', family='monospace',
                bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.9, 
                         edgecolor='#333333', linewidth=1.5))
        
        # Save without tight_layout (can cause issues with 3D plots)
        plt.savefig(self.output_dir / 'pareto_3d.png', dpi=300, bbox_inches='tight', facecolor='white')
        print("  ✓ pareto_3d.png (publication-quality)")
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
        
        # Feature frequency summary
        feature_summary = []
        for feature, count in sorted(self.feature_frequency.items(), key=lambda x: x[1], reverse=True):
            frequency = (count / len(self.trees)) * 100
            feature_summary.append({
                'feature': feature,
                'occurrences': count,
                'frequency_%': frequency,
            })
        
        feature_summary_df = pd.DataFrame(feature_summary)
        feature_summary_df.to_csv(self.output_dir / 'feature_frequency_summary.csv', index=False)
        print("  ✓ feature_frequency_summary.csv")
        
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
        print("3D PARETO ANALYSIS SUMMARY (Feature Frequency Stability)")
        print("="*80)
        print(f"\nTotal Trees: {len(self.trees)}")
        print(f"Frontier Size: {len(frontier)}")
        print(f"\nAccuracy Range: {min(t['accuracy'] for t in self.trees):.0f}% - {max(t['accuracy'] for t in self.trees):.0f}%")
        print(f"Simplicity Range: {min(t['num_features'] for t in self.trees)} - {max(t['num_features'] for t in self.trees)} features")
        print(f"Stability Range: {min(t['stability'] for t in self.trees):.0f}% - {max(t['stability'] for t in self.trees):.0f}%")
        
        print("\n" + "-"*80)
        print("TOP FEATURES (by frequency across 50 runs)")
        print("-"*80)
        
        sorted_features = sorted(self.feature_frequency.items(), key=lambda x: x[1], reverse=True)
        for i, (feature, count) in enumerate(sorted_features[:10], 1):
            freq = (count / len(self.trees)) * 100
            print(f"{i}. {feature}: {count}/50 runs ({freq:.0f}%)")
        
        print("\n" + "-"*80)
        print("TOP FRONTIER TREES")
        print("-"*80)
        
        frontier_sorted = sorted(frontier, key=lambda x: x['accuracy'], reverse=True)
        for i, tree in enumerate(frontier_sorted[:5], 1):
            print(f"\n{i}. Run {tree['run']}")
            print(f"   Accuracy: {tree['accuracy']:.0f}%")
            print(f"   Features: {tree['num_features']} ({tree['feature_set_name']})")
            print(f"   Stability: {tree['stability']:.0f}% (avg frequency of its features)")
        
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
