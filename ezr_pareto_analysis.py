#!/usr/bin/env python3
"""
EZR Pareto Analysis — 2D and 3D
Runs EZR N times, then shows Pareto frontiers. Accuracy is always the primary
axis. Pick 1 or 2 extra dimensions via --dims:
  1 dim  → 2D plot only  (Accuracy × dim1)
  2 dims → 2D + 3D plots (Accuracy × dim1, and Accuracy × dim1 × dim2)

Available dimensions:
  complexity      # features used                         (lower is better)
  stability       avg feature frequency across runs (%)   (higher is better)
  overfitting_gap train accuracy − hold-out accuracy (%)  (lower is better)
  tree_depth      decision levels in the tree             (lower is better)
  coverage        rows reaching the root split            (higher is better)

Usage:
  python3 ezr_pareto_analysis.py --dataset data.csv
  python3 ezr_pareto_analysis.py --dataset data.csv --dims complexity overfitting_gap
  python3 ezr_pareto_analysis.py --dataset data.csv --dims tree_depth stability --runs 30
"""

import subprocess, re, argparse, sys, json
import pandas as pd
from pathlib import Path
from collections import defaultdict


# Registry: dim key → (axis label, maximize)
DIMS = {
    'complexity':      ('Complexity (# Features)',  False),
    'stability':       ('Stability (%)',             True),
    'overfitting_gap': ('Overfitting Gap (%)',       False),
    'tree_depth':      ('Tree Depth (levels)',       False),
    'coverage':        ('Coverage (rows)',            True),
}


# --- EZR Runner ---------------------------------------------------------------

def run_ezr(dataset, n_runs, base_seed):
    """Run EZR n_runs times with different seeds. Returns (trees, feature_counts).

    Each run uses seed = base_seed + run_number, so runs are diverse but
    reproducible: the same --seed always produces the same set of trees.
    """
    trees = []
    feature_counts = defaultdict(int)

    for i in range(1, n_runs + 1):
        seed = base_seed + i
        print(f"[{i}/{n_runs}] Running EZR (seed={seed})...")
        try:
            result = subprocess.run(
                ["ezr", "-f", str(dataset), "-s", str(seed)],
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
                      f"  depth={tree['tree_depth']}  coverage={tree['coverage']}"
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
    """Parse one EZR output into a tree dict.

    Expects repo (github.com/timm/ezr) output format:
      lines[-1]: "Best train: 85 hold-out: 72"
      lines[-2]: "Used: feature1 feature2 feature3"
    Tree body lines: "n:  17   win:  29     if Volume <= 98"
                     "n:   9   win:  40     |  if Volume > 90"
    """
    lines = output.strip().split('\n')
    if len(lines) < 2:
        return None

    # Hold-out accuracy (primary accuracy metric)
    m = re.search(r'hold.out[:\s]+(\d+)', lines[-1])
    if not m:
        return None
    accuracy = int(m.group(1))

    # Train accuracy → overfitting gap
    m_train = re.search(r'train[:\s]+(\d+)', lines[-1])
    train_accuracy = int(m_train.group(1)) if m_train else accuracy
    overfitting_gap = train_accuracy - accuracy

    # Features from "Used: feat1 feat2 ..."
    features = []
    used_line = lines[-2].strip()
    if used_line.startswith('Used:'):
        features = used_line[len('Used:'):].split()

    if not features:  # fallback: scan tree rules for "if feature <op>" patterns
        for line in lines:
            m2 = re.search(r'if\s+(\w+)\s+', line)
            if m2 and m2.group(1) not in features:
                features.append(m2.group(1))

    # Tree depth = max pipe-character depth across all rule lines
    rule_lines = [l for l in lines if re.search(r'if\s+\w+', l)]
    tree_depth = max((l.count('|') for l in rule_lines), default=0) + 1

    # Coverage = n: value at the root node (highest n: across all rule lines)
    n_vals = [int(x) for x in re.findall(r'n:\s*(\d+)', output)]
    coverage = max(n_vals) if n_vals else 0

    return {
        'run':            run_num,
        'accuracy':       accuracy,
        'train_accuracy': train_accuracy,
        'overfitting_gap': overfitting_gap,
        'complexity':     len(features),
        'tree_depth':     tree_depth,
        'coverage':       coverage,
        'features':       features,
        'stability':      0.0,   # filled in by run_ezr after all runs
        'raw_output':     output,
    }


# --- Pareto Logic -------------------------------------------------------------

def pareto_nd(trees, dims):
    """Non-dominated trees across given (key, maximize) dimension pairs.

    A tree b dominates tree a if b is at least as good as a on every
    dimension and strictly better on at least one.
    """
    def dominates(b, a):
        at_least = all(b[k] >= a[k] if mx else b[k] <= a[k] for k, mx in dims)
        strictly  = any(b[k] >  a[k] if mx else b[k] <  a[k] for k, mx in dims)
        return at_least and strictly

    return [a for a in trees if not any(dominates(b, a) for b in trees if b is not a)]


def knee(frontier, dims):
    """Frontier tree with the best normalized balance across all dimensions.

    Each dimension normalized to [0,1]; maximize=False dimensions are flipped.
    The knee is the point closest to the ideal corner (all objectives best).
    """
    vals = {k: [t[k] for t in frontier] for k, _ in dims}

    def score(t):
        scores = []
        for k, maximize in dims:
            lo, hi = min(vals[k]), max(vals[k])
            norm = (t[k] - lo) / max(hi - lo, 1)
            scores.append(norm if maximize else 1 - norm)
        return sum(scores) / len(scores)

    return max(frontier, key=score)


def dims_for(selected):
    """Return (key, maximize) pairs for accuracy + selected extra dims."""
    return [('accuracy', True)] + [(k, DIMS[k][1]) for k in selected]


# --- Output ------------------------------------------------------------------

def save_csv(trees, frontiers, feature_counts, selected_dims, out):
    frontier_sets = {name: set(id(t) for t in f) for name, f in frontiers.items()}
    pd.DataFrame([{
        'run':             t['run'],
        'accuracy':        t['accuracy'],
        'train_accuracy':  t['train_accuracy'],
        'overfitting_gap': t['overfitting_gap'],
        'complexity':      t['complexity'],
        'tree_depth':      t['tree_depth'],
        'coverage':        t['coverage'],
        'stability':       t['stability'],
        'features':        ', '.join(t['features']),
        **{f'on_{name}_frontier': id(t) in fs for name, fs in frontier_sets.items()},
    } for t in trees]).to_csv(out / 'all_trees.csv', index=False)

    n = len(trees)
    pd.DataFrame([{
        'feature':     f,
        'occurrences': c,
        'frequency_%': round(c / n * 100, 1),
    } for f, c in sorted(feature_counts.items(), key=lambda x: -x[1])
    ]).to_csv(out / 'feature_frequency.csv', index=False)


def save_json(trees, frontiers, out):
    def tree_dict(t, rank=None):
        d = {k: v for k, v in t.items() if k != 'features'}
        d['features'] = t['features']
        if rank is not None:
            d['rank'] = rank
        return d

    with open(out / 'all_trees.json', 'w') as f:
        json.dump({'total': len(trees), 'trees': [tree_dict(t) for t in trees]}, f, indent=2)

    for name, frontier in frontiers.items():
        sorted_f = sorted(frontier, key=lambda t: t['accuracy'], reverse=True)
        with open(out / f'pareto_{name}.json', 'w') as f:
            json.dump({
                'frontier_size': len(sorted_f),
                'dimensions':    name,
                'trees': [tree_dict(t, rank=i) for i, t in enumerate(sorted_f, 1)],
            }, f, indent=2)


def plot_2d(trees, frontier, k_pt, dim_x, out):
    import matplotlib.pyplot as plt

    x_label, x_max = DIMS[dim_x]
    off = [t for t in trees if t not in frontier]

    fig, ax = plt.subplots(figsize=(10, 7))

    if off:
        ax.scatter([t[dim_x] for t in off], [t['accuracy'] for t in off],
                   s=80, alpha=0.4, color='#cccccc', edgecolors='#888', linewidth=0.5,
                   label='Off-frontier')
        for t in off:
            ax.annotate(f"R{t['run']}", (t[dim_x], t['accuracy']),
                        xytext=(4, 4), textcoords='offset points',
                        fontsize=7, color='#aaaaaa', alpha=0.8)

    ax.scatter([t[dim_x] for t in frontier], [t['accuracy'] for t in frontier],
               s=150, alpha=0.85, color='#2ecc71', edgecolors='#27ae60', linewidth=1.5,
               label='Pareto frontier')

    sorted_f = sorted(frontier, key=lambda t: t[dim_x])
    ax.plot([t[dim_x] for t in sorted_f], [t['accuracy'] for t in sorted_f],
            'g--', alpha=0.3, linewidth=1)

    for t in frontier:
        ax.annotate(f"Run {t['run']}", (t[dim_x], t['accuracy']),
                    xytext=(5, 5), textcoords='offset points',
                    fontsize=8, fontweight='bold', color='#27ae60')

    ax.scatter([k_pt[dim_x]], [k_pt['accuracy']], s=350, color='#e74c3c',
               marker='*', edgecolors='#c0392b', linewidth=2, zorder=5, label='Knee')

    ax.set_xlabel(x_label, fontsize=12, fontweight='bold')
    ax.set_ylabel('Accuracy (%)', fontsize=12, fontweight='bold')
    ax.set_title(f'2D Pareto Front: Accuracy vs. {x_label}', fontsize=14, fontweight='bold')
    ax.legend(); ax.grid(True, alpha=0.3)
    ax.text(0.02, 0.98, f'Runs: {len(trees)}  |  Frontier: {len(frontier)}',
            transform=ax.transAxes, va='top',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

    plt.tight_layout()
    fname = f'pareto_2d_{dim_x}.png'
    plt.savefig(out / fname, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  {fname}")


def plot_3d(trees, frontier, k_pt, dim_x, dim_y, out):
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d import Axes3D  # noqa: F401 — registers 3d projection
    from matplotlib.colors import Normalize

    x_label, _ = DIMS[dim_x]
    y_label, _ = DIMS[dim_y]
    off = [t for t in trees if t not in frontier]

    fig = plt.figure(figsize=(14, 10), dpi=100)
    ax = fig.add_subplot(111, projection='3d')

    if off:
        ax.scatter([t[dim_x] for t in off], [t[dim_y] for t in off],
                   [t['accuracy'] for t in off],
                   c='#999', s=50, alpha=0.4, edgecolors='#666', linewidth=0.3,
                   label='Off-frontier')

    acc_vals = [t['accuracy'] for t in frontier]
    norm = Normalize(vmin=min(acc_vals), vmax=max(acc_vals))

    unique_xy = set((t[dim_x], t[dim_y]) for t in frontier)
    if len(unique_xy) >= 3:
        ax.plot_trisurf(
            [t[dim_x] for t in frontier], [t[dim_y] for t in frontier],
            [t['accuracy'] for t in frontier],
            cmap='RdYlGn', norm=norm, alpha=0.6,
            edgecolor='#444', linewidth=0.5, shade=True
        )

    sc = ax.scatter(
        [t[dim_x] for t in frontier], [t[dim_y] for t in frontier],
        [t['accuracy'] for t in frontier],
        c=acc_vals, cmap='RdYlGn', norm=norm, s=180, alpha=0.95,
        edgecolors='#1a1a1a', linewidth=1.5, zorder=5
    )
    for i, t in enumerate(sorted(frontier, key=lambda x: x['accuracy'], reverse=True), 1):
        ax.text(t[dim_x], t[dim_y], t['accuracy'], str(i),
                fontsize=10, fontweight='bold', ha='center', va='center', zorder=20)

    ax.scatter([k_pt[dim_x]], [k_pt[dim_y]], [k_pt['accuracy']],
               c='#e74c3c', s=300, marker='*', edgecolors='#c0392b',
               linewidth=2, zorder=10, label='Knee (optimal)')

    plt.colorbar(sc, ax=ax, pad=0.1, shrink=0.7, label='Accuracy (%)')
    ax.set_xlabel(f'\n{x_label}', fontsize=12, fontweight='bold', labelpad=8)
    ax.set_ylabel(f'\n{y_label}', fontsize=12, fontweight='bold', labelpad=8)
    ax.set_zlabel('\nAccuracy (%)', fontsize=12, fontweight='bold', labelpad=8)
    ax.zaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f'{v:.0f}%'))
    ax.set_title(f'3D Pareto Front: Accuracy × {x_label} × {y_label}',
                 fontsize=14, fontweight='bold', pad=20)
    ax.legend(); ax.view_init(elev=25, azim=45)
    ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.5)
    ax.xaxis.pane.fill = ax.yaxis.pane.fill = ax.zaxis.pane.fill = False

    plt.tight_layout()
    fname = f'pareto_3d_{dim_x}_{dim_y}.png'
    plt.savefig(out / fname, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"  {fname}")


def print_summary(trees, frontiers, knees, selected_dims, feature_counts):
    n = len(trees)
    print(f"\n{'='*60}")
    print(f"SUMMARY  ({n} runs)")
    print(f"{'='*60}")
    for name, frontier in frontiers.items():
        k = knees[name]
        dims_str = ' × '.join(['accuracy'] + list(selected_dims[:2 if '3d' in name else 1]))
        print(f"\n{name.upper()} Frontier ({dims_str}): {len(frontier)} trees")
        vals = ', '.join(f"{d}={k[d]}" for d in ['accuracy'] + list(selected_dims[:2 if '3d' in name else 1]))
        print(f"  Knee  : Run {k['run']} — {vals}")
    print(f"\nTop Features:")
    for feat, cnt in sorted(feature_counts.items(), key=lambda x: -x[1])[:10]:
        print(f"  {feat}: {cnt}/{n} ({cnt/n*100:.0f}%)")
    print(f"{'='*60}\n")


# --- Main --------------------------------------------------------------------

def main():
    dim_choices = list(DIMS.keys())

    parser = argparse.ArgumentParser(
        description='EZR 2D + 3D Pareto Analysis',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
dimensions: {', '.join(dim_choices)}
  1 dim  → 2D plot  (Accuracy × dim1)
  2 dims → 2D + 3D  (Accuracy × dim1, Accuracy × dim1 × dim2)

examples:
  python3 ezr_pareto_analysis.py --dataset data.csv
  python3 ezr_pareto_analysis.py --dataset data.csv --dims complexity overfitting_gap
  python3 ezr_pareto_analysis.py --dataset data.csv --dims tree_depth
        """
    )
    parser.add_argument('--dataset', required=True, help='Path to dataset CSV')
    parser.add_argument('--runs', type=int, default=50, help='EZR runs (default: 50)')
    parser.add_argument('--seed', type=int, default=1234567891,
                        help='Base random seed; each run uses seed+i (default: 1234567891)')
    parser.add_argument('--output-dir', default='ezr_output', help='Output directory (default: ezr_output)')
    parser.add_argument('--dims', nargs='+', default=['complexity', 'stability'],
                        choices=dim_choices, metavar='DIM',
                        help=f'1 or 2 extra dimensions beyond accuracy (default: complexity stability)')
    args = parser.parse_args()

    if len(args.dims) > 2:
        parser.error('--dims takes at most 2 dimensions')

    dataset = Path(args.dataset)
    if not dataset.exists():
        print(f"Error: {args.dataset} not found"); sys.exit(1)

    out = Path(args.output_dir)
    out.mkdir(exist_ok=True)

    trees, feature_counts = run_ezr(dataset, args.runs, args.seed)
    if not trees:
        print("No trees collected."); sys.exit(1)

    selected = args.dims
    dim_x = selected[0]
    dim_y = selected[1] if len(selected) == 2 else None

    # Build frontiers and knees
    dims_2d = dims_for([dim_x])
    f2d = pareto_nd(trees, dims_2d)
    k2d = knee(f2d, dims_2d)

    frontiers = {'2d': f2d}
    knees     = {'2d': k2d}

    if dim_y:
        dims_3d = dims_for([dim_x, dim_y])
        f3d = pareto_nd(trees, dims_3d)
        k3d = knee(f3d, dims_3d)
        frontiers['3d'] = f3d
        knees['3d']     = k3d

    print("\nSaving outputs...")
    save_csv(trees, frontiers, feature_counts, selected, out)
    print("  all_trees.csv")
    print("  feature_frequency.csv")
    save_json(trees, frontiers, out)
    print("  all_trees.json")
    for name in frontiers:
        print(f"  pareto_{name}.json")

    plot_2d(trees, f2d, k2d, dim_x, out)
    if dim_y:
        plot_3d(trees, f3d, k3d, dim_x, dim_y, out)

    print_summary(trees, frontiers, knees, selected, feature_counts)
    print(f"Results in: {out}/")


if __name__ == '__main__':
    main()
