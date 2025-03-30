import seaborn as sns
import matplotlib.pyplot as plt
import os

def plot_mean_time(csv_data):
    """
    Generates a line plot of mean time per trial by condition and saves it as a PNG file.
    """

    # Define the output file path
    workspace_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
    data_dir = os.path.join(workspace_dir, "data")
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
    workspace_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
    data_dir = os.path.join(workspace_dir, "data")
    output_path = os.path.join(data_dir, "boxplot_conditions.png")

    # Create the boxplot
    plt.figure(figsize=(8, 6))
    sns.boxplot(data=csv_data, x='condition', y='time', palette='Set2')

    # Add labels and title
    plt.xlabel('Condition')
    plt.ylabel('Completion Time (s)')
    plt.title('Completion Time Distribution by Condition')
    plt.grid(axis='y', linestyle='--', alpha=0.7)

    # Save the plot as a PNG file
    plt.savefig(output_path, format='png', dpi=300)
    print(f"Boxplot saved to {output_path}")

    # Close the plot to free memory
    plt.close()
