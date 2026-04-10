"""
Generate visualizations from evaluation results
Creates comparison plots for the research paper
"""
import json
import os

# Try to import matplotlib, provide fallback if not available
try:
    import matplotlib.pyplot as plt
    import numpy as np
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False
    print("Warning: matplotlib not installed. Install with: pip install matplotlib")


def load_results(filepath='ob2/evaluation_results.json'):
    """Load evaluation results from JSON"""
    if not os.path.exists(filepath):
        print(f"ERROR: Results file not found: {filepath}")
        print("Run evaluate_complete.py first to generate results")
        return None
    
    with open(filepath, 'r') as f:
        return json.load(f)


def create_accuracy_comparison(results, output_file='accuracy_comparison.png'):
    """Create bar chart comparing top-1 and top-5 accuracy"""
    if not HAS_MATPLOTLIB:
        print("Skipping accuracy comparison plot (matplotlib not available)")
        return
    
    methods = []
    acc_top1 = []
    acc_top5 = []
    
    for key, data in results.items():
        methods.append(data['method'])
        acc_top1.append(data['accuracy_top1'] * 100)  # Convert to percentage
        acc_top5.append(data['accuracy_top5'] * 100)
    
    x = np.arange(len(methods))
    width = 0.35
    
    fig, ax = plt.subplots(figsize=(12, 6))
    bars1 = ax.bar(x - width/2, acc_top1, width, label='Top-1 Accuracy')
    bars2 = ax.bar(x + width/2, acc_top5, width, label='Top-5 Accuracy')
    
    ax.set_xlabel('Method', fontsize=12)
    ax.set_ylabel('Accuracy (%)', fontsize=12)
    ax.set_title('Accuracy Comparison Across Methods', fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(methods, rotation=45, ha='right')
    ax.legend()
    ax.grid(axis='y', alpha=0.3)
    
    # Add value labels on bars
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.1f}%',
                   ha='center', va='bottom', fontsize=9)
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"✓ Saved accuracy comparison to {output_file}")
    plt.close()


def create_latency_comparison(results, output_file='latency_comparison.png'):
    """Create bar chart comparing average latency"""
    if not HAS_MATPLOTLIB:
        print("Skipping latency comparison plot (matplotlib not available)")
        return
    
    methods = []
    latencies = []
    
    for key, data in results.items():
        methods.append(data['method'])
        latencies.append(data['avg_time_ms'])
    
    fig, ax = plt.subplots(figsize=(12, 6))
    bars = ax.bar(methods, latencies, color='steelblue', alpha=0.7)
    
    ax.set_xlabel('Method', fontsize=12)
    ax.set_ylabel('Average Latency (ms)', fontsize=12)
    ax.set_title('Latency Comparison Across Methods', fontsize=14, fontweight='bold')
    ax.set_xticklabels(methods, rotation=45, ha='right')
    ax.grid(axis='y', alpha=0.3)
    
    # Add value labels
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
               f'{height:.1f}ms',
               ha='center', va='bottom', fontsize=9)
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"✓ Saved latency comparison to {output_file}")
    plt.close()


def create_accuracy_vs_latency_scatter(results, output_file='accuracy_latency_scatter.png'):
    """Create scatter plot of accuracy vs latency"""
    if not HAS_MATPLOTLIB:
        print("Skipping scatter plot (matplotlib not available)")
        return
    
    methods = []
    accuracies = []
    latencies = []
    costs = []
    
    for key, data in results.items():
        methods.append(data['method'])
        accuracies.append(data['accuracy_top1'] * 100)
        latencies.append(data['avg_time_ms'])
        costs.append(data.get('cost_usd', 0))
    
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # Use cost to determine point size (if available)
    sizes = [100 + c * 1000 for c in costs]  # Scale costs for visibility
    
    scatter = ax.scatter(latencies, accuracies, s=sizes, alpha=0.6, 
                        c=range(len(methods)), cmap='viridis')
    
    # Add labels for each point
    for i, method in enumerate(methods):
        ax.annotate(method, (latencies[i], accuracies[i]),
                   xytext=(5, 5), textcoords='offset points',
                   fontsize=9, bbox=dict(boxstyle='round,pad=0.3', 
                                        facecolor='white', alpha=0.7))
    
    ax.set_xlabel('Average Latency (ms)', fontsize=12)
    ax.set_ylabel('Top-1 Accuracy (%)', fontsize=12)
    ax.set_title('Accuracy vs. Latency Tradeoff', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    
    # Add legend for cost if any methods have non-zero cost
    if max(costs) > 0:
        legend_text = f"Point size = cost (max: ${max(costs):.4f})"
        ax.text(0.02, 0.98, legend_text, transform=ax.transAxes,
               fontsize=10, verticalalignment='top',
               bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"✓ Saved accuracy vs latency scatter to {output_file}")
    plt.close()


def create_cost_comparison(results, output_file='cost_comparison.png'):
    """Create bar chart comparing costs (for LLM methods)"""
    if not HAS_MATPLOTLIB:
        print("Skipping cost comparison plot (matplotlib not available)")
        return
    
    # Filter to only methods with non-zero cost
    methods_with_cost = {k: v for k, v in results.items() if v.get('cost_usd', 0) > 0}
    
    if not methods_with_cost:
        print("No methods with non-zero cost, skipping cost comparison")
        return
    
    methods = []
    costs = []
    accuracies = []
    
    for key, data in methods_with_cost.items():
        methods.append(data['method'])
        costs.append(data['cost_usd'])
        accuracies.append(data['accuracy_top1'] * 100)
    
    fig, ax1 = plt.subplots(figsize=(10, 6))
    
    # Cost bars
    x = np.arange(len(methods))
    bars = ax1.bar(x, costs, alpha=0.7, color='coral', label='Cost (USD)')
    ax1.set_xlabel('Method', fontsize=12)
    ax1.set_ylabel('Cost (USD)', fontsize=12, color='coral')
    ax1.tick_params(axis='y', labelcolor='coral')
    ax1.set_xticks(x)
    ax1.set_xticklabels(methods, rotation=45, ha='right')
    
    # Accuracy line
    ax2 = ax1.twinx()
    line = ax2.plot(x, accuracies, 'o-', color='steelblue', 
                   linewidth=2, markersize=8, label='Accuracy (%)')
    ax2.set_ylabel('Top-1 Accuracy (%)', fontsize=12, color='steelblue')
    ax2.tick_params(axis='y', labelcolor='steelblue')
    
    # Title and grid
    ax1.set_title('Cost vs. Accuracy for Paid Methods', fontsize=14, fontweight='bold')
    ax1.grid(axis='y', alpha=0.3)
    
    # Add value labels
    for i, (bar, acc) in enumerate(zip(bars, accuracies)):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height,
                f'${height:.4f}',
                ha='center', va='bottom', fontsize=9)
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"✓ Saved cost comparison to {output_file}")
    plt.close()


def create_summary_table(results, output_file='results_table.txt'):
    """Create a formatted text table of results"""
    lines = []
    lines.append("="*120)
    lines.append("EVALUATION RESULTS SUMMARY TABLE")
    lines.append("="*120)
    lines.append(f"{'Method':<35} {'Top-1':<10} {'Top-5':<10} {'Latency':<15} {'Cost':<12} {'Samples':<10}")
    lines.append("-"*120)
    
    for key, data in results.items():
        method = data['method']
        acc1 = f"{data['accuracy_top1']:.2%}"
        acc5 = f"{data['accuracy_top5']:.2%}"
        latency = f"{data['avg_time_ms']:.2f} ms"
        cost = f"${data.get('cost_usd', 0):.4f}" if data.get('cost_usd', 0) > 0 else "$0.00"
        samples = str(data['n_examples'])
        
        lines.append(f"{method:<35} {acc1:<10} {acc5:<10} {latency:<15} {cost:<12} {samples:<10}")
    
    lines.append("="*120)
    
    # Write to file
    with open(output_file, 'w') as f:
        f.write('\n'.join(lines))
    
    # Also print to console
    print('\n'.join(lines))
    print(f"\n✓ Saved results table to {output_file}")


def main():
    """Generate all visualizations"""
    print("="*80)
    print("GENERATING VISUALIZATIONS FROM EVALUATION RESULTS")
    print("="*80)
    
    # Load results
    results = load_results()
    if not results:
        return
    
    print(f"\nLoaded results for {len(results)} methods")
    
    # Create visualizations
    create_accuracy_comparison(results)
    create_latency_comparison(results)
    create_accuracy_vs_latency_scatter(results)
    create_cost_comparison(results)
    create_summary_table(results)
    
    print("\n" + "="*80)
    print("✅ VISUALIZATION GENERATION COMPLETE")
    print("="*80)
    print("\nGenerated files:")
    output_files = [
        'accuracy_comparison.png',
        'latency_comparison.png',
        'accuracy_latency_scatter.png',
        'cost_comparison.png',
        'results_table.txt'
    ]
    for f in output_files:
        if os.path.exists(f):
            print(f"  ✓ {f}")


if __name__ == "__main__":
    main()
