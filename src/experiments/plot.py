from __future__ import annotations

from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt


def plot_runtime(summary_csv: Path, out_png: Path) -> None:
    s = pd.read_csv(summary_csv)

    # Ensure numeric
    s["n"] = pd.to_numeric(s["n"], errors="coerce")
    s["time_median"] = pd.to_numeric(s["time_median"], errors="coerce")
    s["time_p90"] = pd.to_numeric(s["time_p90"], errors="coerce")

    # Plot one line per approach
    plt.figure(figsize=(12, 6))
    for approach in sorted(s["approach"].dropna().unique()):
        sub = s[s["approach"] == approach].sort_values("n")
        plt.plot(sub["n"], sub["time_median"], marker="o", label=approach)

    plt.xlabel("N", fontsize=12)
    plt.ylabel("Median runtime (s)", fontsize=12)
    plt.title("Runtime vs N (median)", fontsize=14, fontweight='bold')
    plt.legend(fontsize=10)
    out_png.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out_png, dpi=200, bbox_inches="tight")
    plt.close()

def plot_success_rate(summary_csv: Path, out_png: Path) -> None:
    s = pd.read_csv(summary_csv)

    s["n"] = pd.to_numeric(s["n"], errors="coerce")
    s["valid_rate"] = pd.to_numeric(s["valid_rate"], errors="coerce")

    plt.figure()
    for approach in sorted(s["approach"].dropna().unique()):
        sub = s[s["approach"] == approach].sort_values("n")
        plt.plot(sub["n"], sub["valid_rate"], marker="o", label=approach)

    plt.xlabel("N")
    plt.ylabel("Valid rate")
    plt.title("Solution validity rate vs N")
    plt.ylim(-0.05, 1.05)
    plt.legend()
    out_png.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out_png, dpi=200, bbox_inches="tight")
    plt.close()


def plot_failure_threshold(summary_csv: Path, out_png: Path) -> None:
    """
    Plot success/failure for each tested N value per approach.
    Shows discrete tested N values with clear success/failure indicators.
    """
    s = pd.read_csv(summary_csv)

    # Ensure numeric
    s["n"] = pd.to_numeric(s["n"], errors="coerce")
    s["valid_rate"] = pd.to_numeric(s["valid_rate"], errors="coerce")

    # Create readable labels
    label_map = {
        "cp_boolean": "CP Boolean",
        "cp_integer_alldiff": "CP Integer",
        "qubo_amplify": "QUBO Amplify",
    }

    # Get all tested N values (sorted, unique)
    all_ns = sorted(s["n"].dropna().unique())
    
    # Organize data by approach
    approach_data = {}
    for approach in sorted(s["approach"].dropna().unique()):
        sub = s[s["approach"] == approach].sort_values("n")
        approach_data[approach] = {}
        for _, row in sub.iterrows():
            n_val = int(row["n"])
            valid_rate = row["valid_rate"]
            # Success if valid_rate >= 1.0
            approach_data[approach][n_val] = valid_rate >= 1.0

    # Create figure
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Create y-positions for each approach
    approaches = sorted(approach_data.keys())
    y_positions = {approach: i for i, approach in enumerate(approaches)}
    labels = [label_map.get(a, a) for a in approaches]
    
    # Plot markers for each tested N
    success_plotted = False
    failure_plotted = False
    
    for approach in approaches:
        y_pos = y_positions[approach]
        for n_val in all_ns:
            if n_val in approach_data[approach]:
                is_success = approach_data[approach][n_val]
                # Green filled circle for success, red X for failure
                if is_success:
                    label = 'Success' if not success_plotted else ''
                    ax.scatter(n_val, y_pos, s=200, marker='o', 
                             color='#2ecc71', edgecolors='darkgreen', 
                             linewidths=2, zorder=3, label=label)
                    if not success_plotted:
                        success_plotted = True
                else:
                    label = 'Failure' if not failure_plotted else ''
                    ax.scatter(n_val, y_pos, s=200, marker='x', 
                             color='#e74c3c', linewidths=3, zorder=3, label=label)
                    if not failure_plotted:
                        failure_plotted = True
    
    # Set y-axis
    ax.set_yticks(range(len(approaches)))
    ax.set_yticklabels(labels)
    ax.set_ylabel("Approach", fontsize=12)
    
    # Set x-axis to show only tested N values
    # Show all ticks but only label specific values
    ax.set_xticks(all_ns)
    
    # Only show labels for specific N values
    label_ns = {8, 30, 60, 100, 150, 300, 500}
    x_labels = []
    for n in all_ns:
        if int(n) in label_ns:
            x_labels.append(str(int(n)))
        else:
            x_labels.append('')
    ax.set_xticklabels(x_labels)
    ax.set_xlabel("N (tested values)", fontsize=12)
    
    # Add grid
    ax.grid(axis='x', alpha=0.3, linestyle='--', zorder=0)
    ax.grid(axis='y', alpha=0.2, linestyle='-', zorder=0)
    
    # Set title
    ax.set_title("Failure Threshold: Success/Failure by Tested N Values", 
                fontsize=14, fontweight='bold')
    
    # Add legend
    ax.legend(loc='upper right')
    
    # Set limits with wider side margins to see full markers
    min_n = min(all_ns)
    max_n = max(all_ns)
    # Add more padding on sides (about 8% of range on each side)
    padding = max(3, (max_n - min_n) * 0.08)
    ax.set_xlim(min_n - padding, max_n + padding)
    ax.set_ylim(-0.5, len(approaches) - 0.5)
    
    plt.tight_layout()
    out_png.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out_png, dpi=200, bbox_inches="tight")
    plt.close()
