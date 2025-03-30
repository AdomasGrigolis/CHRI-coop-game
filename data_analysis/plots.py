import seaborn as sns
import matplotlib.pyplot as plt
import os

workspace_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
data_dir = os.path.join(workspace_dir, "data")

def plot_mean_time(csv_data):
    """
    Generates a line plot of mean time per trial by condition and saves it as a PNG file.
    """

    # Define the output file path
    output_path = os.path.join(data_dir, "mean_time_per_trial.png")

    # Filter out rows where time is 0
    filtered_data = csv_data[csv_data['time'] != 0]

    # Group by trial_number and condition, and calculate the mean time
    grouped_data = filtered_data.groupby(['trial_number', 'condition'], as_index=False)['time'].mean()

    # Convert condition names
    grouped_data['condition'] = grouped_data['condition'].replace({'H': 'Haptic', 'M': 'Mouse'})

    # Create the line plot
    plt.figure(figsize=(10, 6))
    sns.lineplot(data=grouped_data, x='trial_number', y='time', hue='condition', marker='o')

    # Add labels and title
    plt.xlabel('Trial Number')
    plt.ylabel('Mean Time (s)')
    plt.title('Mean Time per Trial by Condition')
    plt.legend(title='Condition')
    plt.grid(True)
    plt.tight_layout()

    plt.xticks(ticks=grouped_data['trial_number'].unique(), labels=grouped_data['trial_number'].unique())

    # Save the plot as a PNG file
    plt.savefig(output_path, format='png', dpi=300)
    print(f"Plot saved to {output_path}")

    # Close the plot to free memory
    plt.close()

def plot_boxplot_conditions(csv_data):
    """
    Generates a boxplot showing the distribution of completion times for each condition (Haptic and Mouse).
    Saves the plot as a PNG file in the data directory.
    """

    # Define the output file path
    output_path = os.path.join(data_dir, "boxplot_conditions.png")

    csv_data = csv_data.copy()
    # Convert condition names
    csv_data['condition'] = csv_data['condition'].replace({'H': 'Haptic', 'M': 'Mouse'})

    # Create the boxplot
    plt.figure(figsize=(8, 6))
    sns.boxplot(data=csv_data, x='condition', y='time', palette='Set2')

    # Add labels and title
    plt.xlabel('Condition')
    plt.ylabel('Completion Time (s)')
    plt.title('Completion Time Distribution by Condition')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()

    # Save the plot as a PNG file
    plt.savefig(output_path, format='png', dpi=300)
    print(f"Boxplot saved to {output_path}")

    # Close the plot to free memory
    plt.close()

def plot_wdq_analysis(wdq_stats):
    """
    Generates a grouped bar chart comparing WDQ metrics (realism, autonomy/significance, and engagement) across conditions.
    Saves the plot as a PNG file.
    """

    # Define the output file path
    output_path = os.path.join(data_dir, "wdq_analysis.png")

    # Extract data for plotting
    metrics = ["autonomy_score", "significance_score", "engagement_score"]
    descriptive_labels = ["Autonomy", "Significance", "Engagement"]
    conditions = ["Haptic", "Mouse"]
    scores = {
        metric: [wdq_stats[metric]["haptic_mean"], wdq_stats[metric]["mouse_mean"]]
        for metric in metrics
    }

    # Create the grouped bar chart
    x = range(len(metrics))
    bar_width = 0.35

    plt.figure(figsize=(10, 6))
    for i, condition in enumerate(conditions):
        plt.bar(
            [p + i * bar_width for p in x],
            [scores[metric][i] for metric in metrics],
            width=bar_width,
            label=condition
        )

    # Add labels and title
    plt.ylabel("Mean Score")
    plt.title("WDQ Metrics Comparison Across Conditions")
    plt.xticks([p + bar_width / 2 for p in x], descriptive_labels, rotation=45, ha="right")
    plt.legend(title="Condition")
    plt.grid(axis="y", linestyle="--", alpha=0.7)
    plt.tight_layout()

    # Save the plot as a PNG file
    plt.savefig(output_path, format="png", dpi=300)
    print(f"WDQ analysis plot saved to {output_path}")

    # Close the plot to free memory
    plt.close()

def plot_nasa_metrics(questionnaire_data):
    """
    Generates a grouped bar chart comparing NASA metrics (Mental demand, Physical demand, etc.)
    across conditions (Haptic and Mouse). Saves the plot as a PNG file.
    """

    # Define the output file path
    output_path = os.path.join(data_dir, "nasa_metrics_comparison.png")

    # Extract relevant columns for NASA metrics
    nasa_columns = ["NASA_1", "NASA_2", "NASA_3", "NASA_4", "NASA_5", "NASA_6"]
    descriptive_labels = [
        "Mental demand", "Physical demand", "Temporal demand",
        "Performance", "Effort", "Frustration level"
    ]

    # Group by condition and calculate the mean for NASA metrics
    grouped_data = questionnaire_data.groupby("condition")[nasa_columns].mean().reset_index()

    # Extract conditions and scores
    conditions = grouped_data["condition"].replace({"H": "Haptic", "M": "Mouse"}).values
    scores = {metric: grouped_data[metric].values for metric in nasa_columns}

    # Create the grouped bar chart
    x = range(len(nasa_columns))
    bar_width = 0.35

    plt.figure(figsize=(12, 6))
    for i, condition in enumerate(conditions):
        plt.bar(
            [p + i * bar_width for p in x],
            [scores[metric][i] for metric in nasa_columns],
            width=bar_width,
            label=condition
        )

    # Add labels and title
    plt.ylabel("Mean Score")
    plt.title("NASA Metrics Comparison Across Conditions")
    plt.xticks([p + bar_width / 2 for p in x], descriptive_labels, rotation=45, ha="right")
    plt.legend(title="Condition")
    plt.grid(axis="y", linestyle="--", alpha=0.7)
    plt.tight_layout()

    # Save the plot as a PNG file
    plt.savefig(output_path, format="png", dpi=300)
    print(f"NASA metrics comparison plot saved to {output_path}")

    # Close the plot to free memory
    plt.close()