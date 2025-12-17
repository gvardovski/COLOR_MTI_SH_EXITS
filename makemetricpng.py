import matplotlib.pyplot as plt
import seaborn as sns
import os

def create_heatmap(
    results_df,
    metric_name,
    index_col='Days',
    column_col=None,
    output_dir='data/',
    figsize=(20, 14)
):
    try:
        print(f"\n>>> Creating heatmap for: {metric_name}")

        if metric_name not in results_df.columns:
            print(f"WARNING: '{metric_name}' not found. Skipping...")
            return False

        if column_col is None:
            print("WARNING: column_col not provided (need 2D optimization). Skipping...")
            return False

        heatmap_data = results_df.pivot_table(
            index=index_col,
            columns=column_col,
            values=metric_name,
            aggfunc='mean'
        )

        if heatmap_data.empty or heatmap_data.isna().all().all():
            print(f"WARNING: No valid data for '{metric_name}'. Skipping...")
            return False

        valid_values = heatmap_data.stack().dropna()
        print(
            f"  Valid values: {len(valid_values)} | "
            f"Min: {valid_values.min():.2f} | "
            f"Max: {valid_values.max():.2f} | "
            f"Mean: {valid_values.mean():.2f}"
        )

        annot = heatmap_data.size <= 100
        center = 0 if valid_values.min() < 0 else None

        plt.figure(figsize=figsize)
        sns.heatmap(
            heatmap_data,
            cmap='coolwarm',
            annot=annot,
            fmt=".2f",
            center=center,
            cbar_kws={'label': metric_name}
        )

        plt.title(f"{metric_name} Heatmap")
        plt.xlabel(column_col)
        plt.ylabel(index_col)
        plt.tight_layout()

        os.makedirs(output_dir, exist_ok=True)
        safe_name = metric_name.replace('%', 'pct').replace('/', '_')
        filepath = os.path.join(output_dir, f"{safe_name}.png")

        plt.savefig(filepath, dpi=150)
        plt.close()

        print(f"  ✓ Saved: {filepath}")
        return True

    except Exception as e:
        print(f"ERROR creating heatmap for '{metric_name}': {e}")
        plt.close()
        return False