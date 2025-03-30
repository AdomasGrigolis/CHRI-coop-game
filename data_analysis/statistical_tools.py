from scipy.stats import ttest_rel, linregress
import pandas as pd
import numpy as np

def analyze_task_completion(csv_data):
    """
    Analyzes task completion times for Haptic and Mouse conditions.
    """
    # Filter data by condition
    haptic_data = csv_data[csv_data['condition'] == 'H']['time']
    mouse_data = csv_data[csv_data['condition'] == 'M']['time']

    # Calculate mean and standard deviation
    haptic_mean = haptic_data.mean()
    haptic_std = haptic_data.std()
    mouse_mean = mouse_data.mean()
    mouse_std = mouse_data.std()

    # Perform paired t-test
    from scipy.stats import ttest_rel
    t_stat, p_value = ttest_rel(
        csv_data[csv_data['condition'] == 'H']['time'].values,
        csv_data[csv_data['condition'] == 'M']['time'].values
    )

    return {
        "haptic_mean": haptic_mean,
        "haptic_std": haptic_std,
        "mouse_mean": mouse_mean,
        "mouse_std": mouse_std,
        "t_stat": t_stat,
        "p_value": p_value
    }

def analyze_learning_curve(csv_data):
    """
    Analyzes the learning curve (downwards trend) for Haptic and Mouse conditions.
    Compares the slope of completion time across trials for each condition.
    """

    # Filter data by condition
    haptic_data = csv_data[csv_data['condition'] == 'H']
    mouse_data = csv_data[csv_data['condition'] == 'M']

    # Group by trial_number and calculate mean time for each condition
    haptic_grouped = haptic_data.groupby('trial_number')['time'].mean().reset_index()
    mouse_grouped = mouse_data.groupby('trial_number')['time'].mean().reset_index()

    # Perform linear regression for each condition
    haptic_slope, haptic_intercept, _, _, _ = linregress(haptic_grouped['trial_number'], haptic_grouped['time'])
    mouse_slope, mouse_intercept, _, _, _ = linregress(mouse_grouped['trial_number'], mouse_grouped['time'])

    # Compare slopes
    if abs(haptic_slope) > abs(mouse_slope):
        print("The haptic condition shows a stronger learning curve (steeper downward trend) compared to the mouse condition.")
    else:
        print("The mouse condition shows a stronger learning curve (steeper downward trend) compared to the haptic condition.")

    return {
        "haptic_slope": haptic_slope,
        "mouse_slope": mouse_slope,
    }