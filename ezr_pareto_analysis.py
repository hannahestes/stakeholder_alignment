#!/usr/bin/env python3
"""
EZR Pareto Analysis — 2D and 3D
Runs EZR N times, then shows Pareto frontiers for:
  2D: Accuracy × Complexity
  3D: Accuracy × Complexity × Stability (feature frequency)

Usage:
    python3 ezr_pareto_analysis.py --runs 50 --dataset data.csv --output-dir results/
"""

import subprocess, re, argparse, sys, json
import pandas as pd
from pathlib import Path
from collections import defaultdict


# --- EZR Runner ---------------------------------------------------------------

def run_ezr(dataset, n_runs):
    """Run EZR n_runs times. Returns (trees, feature_counts)."""
    trees = []
    feature_counts = defaultdict(int)

    for i in range(1, n_runs + 1):
        print(f"[{i}/{n_runs}] Running EZR...")
        try:
            result = subprocess.run(
                ["ezr", "-f", str(dataset)],
                capture_output=True, text=True, timeout=60
            )
            if result.returncode != 0:
                print(f"  Warning: run failed"); continue

            tree = parse(result.stdout, i)
            if tree:
                trees.append(tree)
                for f in tree['features']:
                    feature_counts[f] += 1
                print(f"  accuracy={tree['accuracy']}  complexity={tree['complexity']}"
                      f"  features={', '.join(tree['features'])}")
        except Exception as e:
            print(f"  Warning: {e}")

    # Stability = avg frequency of a tree's features across all runs
    n = len(trees)
    for tree in trees:
        if tree['features']:
            avg = sum(feature_counts[f] for f in tree['features']) / len(tree['features'])
            tree['stability'] = round((avg / n) * 100, 1)
        else:
            tree['stability'] = 0.0

    return trees, dict(feature_counts)


def parse(output, run_num):
    """Parse one EZR output into a tree dict."""
    lines = output.strip().split('\n')
    if len(lines) < 2:
        return None

    try:
        accuracy = int(lines[-1].strip().split()[-1])
    except (ValueError, IndexError):
        return None

    features, complexity = [], 0
    parts = lines[-2].strip().split(maxsplit=2)
    if len(parts) >= 3:
        try:
            complexity = int(parts[1])
            features = [f.strip().rstrip(',') for f in parts[2].split(',') if f.strip()]
        except ValueError:
            pass

    if not features:  # fallback: scan for "if feature ==" patterns
        for line in lines:
            m = re.search(r'if\s+(\w+)\s+==', line)
            if m and m.group(1) not in features:
                features.append(m.group(1))
        complexity = len(features)

    return {'run': run_num, 'accuracy': accuracy, 'complexity': complexity,
            'features': features, 'raw_output': output}


# --- Pareto Logic -------------------------------------------------------------

def pareto_2d(trees):
    """Non-dominated trees on accuracy × complexity."""
    return [a for a in trees if not any(
        b['accuracy'] >= a['accuracy'] and b['complexity'] <= a['complexity'] and
        (b['accuracy'] > a['accuracy'] or b['complexity'] < a['complexity'])
        for b in trees if b is not a
    )]


def pareto_3d(trees):
    """Non-dominated trees on accuracy × complexity × stability."""
    return [a for a in trees if not any(
        b['accuracy'] >= a['accuracy'] and b['complexity'] <= a['complexity'] and
        b['stability'] >= a['stability'] and
        (b['accuracy'] > a['accuracy'] or b['complexity'] < a['complexity']
         or b['stability'] > a['stability'])
        for b in trees if b is not a
    )]


def knee_2d(frontier):
    """Simplest tree with best accuracy on the 2D frontier."""
    min_c = min(t['complexity'] for t in frontier)
    return max((t for t in frontier if t['complexity'] == min_c), key=lambda t: t['accuracy'])


def knee_3d(frontier):
    """Best normalized balance across all 3 dimensions."""
    acc = [t['accuracy'] for t in frontier]
    cmp = [t['complexity'] for t in frontier]
    stb = [t['stability'] for t in frontier]

    def score(t):
        na = (t['accuracy'] - min(acc)) / max(max(acc) - min(acc), 1)
        nc = 1 - (t['complexity'] - min(cmp)) / max(max(cmp) - min(cmp), 1)
        ns = (t['stability'] - min(stb)) / max(max(stb) - min(stb), 1)
        return (na + nc + ns) / 3

    return max(frontier, key=score)


# --- Output ------------------------------------------------------------------

def save_csv(trees, f2d, f3d, feature_counts, out):
    pd.DataFrame([{
        'run':            t['run'],
        'accuracy':       t['accuracy'],
        'complexity':     t['complexity'],
        'stability':      t['stability'],
        'features':       ', '.join(t['features']),
        'on_2d_frontier': t in f2d,
        'on_3d_frontier': t in f3d,
    } for t in trees]).to_csv(out / 'all_trees.csv', index=False)

    n = len(trees)
    pd.DataFrame([{
        'feature':     f,
        'occurrences': c,
        'frequency_%': round(c / n * 100, 1),
    } for f, c in sorted(feature_counts.items(), key=lambda x: -x[1])
    ]).to_csv(out / 'feature_frequency.csv', index=False)


def save_json(trees, f2d, f3d, out):
    def tree_dict(t, rank=None):
        d = {
            'run':        t['run'],
            'accuracy':   t['accuracy'],
            'complexity': t['complexity'],
            'stability':  t['stability'],
            'features':   t['features'],
            'raw_output': t['raw_output'],
        }
        if rank is not None:
            d['rank'] = rank
        return d

    with open(out / 'all_trees.json', 'w') as f:
        json.dump({'total': len(trees), 'trees': [tree_dict(t) for t in trees]}, f, indent=2)

    f2d_sorted = sorted(f2d, key=lambda t: t['accuracy'], reverse=True)
    with open(out / 'pareto_2d.json', 'w') as f:
        json.dump({'frontier_size': len(f2d_sorted),
                   'trees': [tree_dict(t, rank=i) for i, t in enumerate(f2d_sorted, 1)]},
                  f, indent=2)

    f3d_sorted = sorted(f3d, key=lambda t: t['accuracy'], reverse=True)
    with open(out / 'pareto_3d.json', 'w') as f:
        json.dump({'frontier_size': len(f3d_sorted),
                   'trees': [tree_dict(t, rank=i) for i, t in enumerate(f3d_sorted, 1)]},
                  f, indent=2)


def plot_2d(trees, frontier, knee, out):
    import matplotlib.pyplot as plt

    off = [t for t in trees if t not in frontier]
    fig, ax = plt.subplots(figsize=(10, 7))

    if off:
        ax.scatter([t['complexity'] for t in off], [t['accuracy'] for t in off],
                   s=80, alpha=0.4, color='#cccccc', edgecolors='#888', linewidth=0.5,
                   label='Off-frontier')
        for t in off:
            ax.annotate(f"R{t['run']}", (t['complexity'], t['accuracy']),
                        xytext=(4, 4), textcoords='offset points', fontsize=7,
                        color='#aaaaaa', alpha=0.8)

    ax.scatter([t['complexity'] for t in frontier], [t['accuracy'] for t in frontier],
               s=150, alpha=0.85, color='#2ecc71', edgecolors='#27ae60', linewidth=1.5,
               label='Pareto frontier')

    sorted_f = sorted(frontier, key=lambda t: t['complexity'])
    ax.plot([t['complexity'] for t in sorted_f], [t['accuracy'] for t in sorted_f],
            'g--', alpha=0.3, linewidth=1)

    for t in frontier:
        ax.annotate(f"Run {t['run']}", (t['complexity'], t['accuracy']),
                    xytext=(5, 5), textcoords='offset points', fontsize=8,
                    fontweight='bold', color='#27ae60')

    ax.scatter([knee['complexity']], [knee['accuracy']], s=350, color='#e74c3c',
               marker='*', edgecolors='#c0392b', linewidth=2, zorder=5, label='Knee')

    ax.set_xlabel('Complexity (# Features)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Accuracy (%)', fontsize=12, fontweight='bold')
    ax.set_title('2D Pareto Front: Accuracy vs. Complexity', fontsize=14, fontweight='bold')
    ax.legend(); ax.grid(True, alpha=0.3)
    ax.text(0.02, 0.98, f'Runs: {len(trees)}  |  Frontier: {len(frontier)}',
            transform=ax.transAxes, va='top',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

    plt.tight_layout()
    plt.savefig(out / 'pareto_2d.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("  pareto_2d.png")


def plot_3d(trees, frontier, knee, out):
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d import Axes3D  # noqa: F401 — registers 3d projection
    from matplotlib.colors import Normalize

    off = [t for t in trees if t not in frontier]
    fig = plt.figure(figsize=(14, 10), dpi=100)
    ax = fig.add_subplot(111, projection='3d')

    if off:
        ax.scatter([t['complexity'] for t in off], [t['stability'] for t in off],
                   [t['accuracy'] for t in off],
                   c='#999', s=50, alpha=0.4, edgecolors='#666', linewidth=0.3,
                   label='Off-frontier')

    acc_vals = [t['accuracy'] for t in frontier]
    norm = Normalize(vmin=min(acc_vals), vmax=max(acc_vals))

    if len(frontier) >= 3:
        ax.plot_trisurf(
            [t['complexity'] for t in frontier],
            [t['stability'] for t in frontier],
            [t['accuracy'] for t in frontier],
            cmap='RdYlGn', norm=norm, alpha=0.6,
            edgecolor='#444', linewidth=0.5, shade=True
        )

    sc = ax.scatter(
        [t['complexity'] for t in frontier], [t['stability'] for t in frontier],
        [t['accuracy'] for t in frontier],
        c=acc_vals, cmap='RdYlGn', norm=norm, s=180, alpha=0.95,
        edgecolors='#1a1a1a', linewidth=1.5, zorder=5
    )
    for i, t in enumerate(sorted(frontier, key=lambda x: x['accuracy'], reverse=True), 1):
        ax.text(t['complexity'], t['stability'], t['accuracy'], str(i),
                fontsize=10, fontweight='bold', ha='center', va='center', zorder=20)

    ax.scatter([knee['complexity']], [knee['stability']], [knee['accuracy']],
               c='#e74c3c', s=700, marker='*', edgecolors='#c0392b',
               linewidth=2, zorder=10, label='Knee (optimal)')

    plt.colorbar(sc, ax=ax, pad=0.1, shrink=0.7, label='Accuracy (%)')
    ax.set_xlabel('\nComplexity (# Features)', fontsize=12, fontweight='bold', labelpad=8)
    ax.set_ylabel('\nStability (%)', fontsize=12, fontweight='bold', labelpad=8)
    ax.set_zlabel('\nAccuracy (%)', fontsize=12, fontweight='bold', labelpad=8)
    ax.zaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f'{v:.0f}%'))
    ax.set_title('3D Pareto Front: Accuracy × Complexity × Stability',
                 fontsize=14, fontweight='bold', pad=20)
    ax.legend(); ax.view_init(elev=25, azim=45)
    ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.5)
    ax.xaxis.pane.fill = ax.yaxis.pane.fill = ax.zaxis.pane.fill = False

    plt.tight_layout()
    plt.savefig(out / 'pareto_3d.png', dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    print("  pareto_3d.png")


def print_summary(trees, f2d, f3d, k2d, k3d, feature_counts):
    n = len(trees)
    print(f"\n{'='*60}")
    print(f"SUMMARY  ({n} runs)")
    print(f"{'='*60}")
    print(f"2D Frontier : {len(f2d)} trees")
    print(f"  Knee      : Run {k2d['run']} — {k2d['complexity']} features, {k2d['accuracy']}% accuracy")
    print(f"3D Frontier : {len(f3d)} trees")
    print(f"  Knee      : Run {k3d['run']} — {k3d['complexity']} features, "
          f"{k3d['accuracy']}% accuracy, {k3d['stability']}% stability")
    print(f"\nTop Features:")
    for feat, cnt in sorted(feature_counts.items(), key=lambda x: -x[1])[:10]:
        print(f"  {feat}: {cnt}/{n} ({cnt/n*100:.0f}%)")
    print(f"{'='*60}\n")


# --- Main --------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description='EZR 2D + 3D Pareto Analysis')
    parser.add_argument('--dataset', required=True, help='Path to dataset CSV')
    parser.add_argument('--runs', type=int, default=50, help='EZR runs (default: 50)')
    parser.add_argument('--output-dir', default='ezr_output', help='Output directory (default: ezr_output)')
    args = parser.parse_args()

    dataset = Path(args.dataset)
    if not dataset.exists():
        print(f"Error: {args.dataset} not found"); sys.exit(1)

    out = Path(args.output_dir)
    out.mkdir(exist_ok=True)

    trees, feature_counts = run_ezr(dataset, args.runs)
    if not trees:
        print("No trees collected."); sys.exit(1)

    f2d, f3d = pareto_2d(trees), pareto_3d(trees)
    k2d, k3d = knee_2d(f2d), knee_3d(f3d)

    print("\nSaving outputs...")
    save_csv(trees, f2d, f3d, feature_counts, out)
    print("  all_trees.csv")
    print("  feature_frequency.csv")
    save_json(trees, f2d, f3d, out)
    print("  all_trees.json")
    print("  pareto_2d.json")
    print("  pareto_3d.json")

    plot_2d(trees, f2d, k2d, out)
    plot_3d(trees, f3d, k3d, out)

    print_summary(trees, f2d, f3d, k2d, k3d, feature_counts)
    print(f"Results in: {out}/")


if __name__ == '__main__':
    main()
