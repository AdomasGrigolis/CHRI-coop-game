from scipy.stats import ttest_rel, linregress, ttest_ind, wilcoxon
import pandas as pd
import numpy as np

from scipy.stats import wilcoxon

def analyze_task_completion(csv_data):
    """
    Analyzes task completion times for Haptic and Mouse conditions using the Wilcoxon Signed-Rank Test.
    """

    csv_data = csv_data.copy()

    # Ensure the data is paired by participant_id and trial_number
    paired_data = csv_data.pivot(index=['participant_id', 'trial_number'], columns='condition', values='time').dropna()

    # Extract paired data for Haptic and Mouse conditions
    haptic_times = paired_data['H']
    mouse_times = paired_data['M']

    # Calculate mean and standard deviation
    haptic_mean = haptic_times.mean()
    haptic_std = haptic_times.std()
    mouse_mean = mouse_times.mean()
    mouse_std = mouse_times.std()

    # Perform Wilcoxon Signed-Rank Test
    if len(haptic_times) > 0 and len(mouse_times) > 0:
        w_stat, p_value = wilcoxon(haptic_times, mouse_times)
    else:
        w_stat, p_value = np.nan, np.nan  # Not enough data for the test

    return {
        "haptic_mean": haptic_mean,
        "haptic_std": haptic_std,
        "mouse_mean": mouse_mean,
        "mouse_std": mouse_std,
        "w_stat": w_stat,
        "p_value": p_value
    }

def analyze_learning_curve(csv_data):
    """
    Analyzes the learning curve (downwards trend) for Haptic and Mouse conditions using the Wilcoxon Signed-Rank Test.
    Compares the slope of completion time across trials for each condition.
    """

    csv_data = csv_data.copy()

    # Filter data by condition
    haptic_data = csv_data[csv_data['condition'] == 'H']
    mouse_data = csv_data[csv_data['condition'] == 'M']

    # Group by trial_number and calculate mean time for each condition
    haptic_grouped = haptic_data.groupby('trial_number')['time'].mean()
    mouse_grouped = mouse_data.groupby('trial_number')['time'].mean()

    # Perform Wilcoxon Signed-Rank Test on trial-level means
    if len(haptic_grouped) > 0 and len(mouse_grouped) > 0 and len(haptic_grouped) == len(mouse_grouped):
        w_stat, p_value = wilcoxon(haptic_grouped, mouse_grouped)
    else:
        w_stat, p_value = np.nan, np.nan  # Not enough data or unequal group sizes

    return {
        "haptic_slope": haptic_grouped.mean(),  # Approximation for slope
        "mouse_slope": mouse_grouped.mean(),   # Approximation for slope
        "w_stat": w_stat,
        "p_value": p_value
    }

def analyze_nasa_and_stress(questionnaire_data):
    """
    Analyzes questionnaire data for ease of grasping (Q2), overall workload (NASA-TLX),
    and stress (focused on NASA-TLX categories: Mental Demand, Frustration, and Effort).
    """

    questionnaire_data = questionnaire_data.copy()

    # Compute NASA-TLX score as the average of NASA_1 to NASA_6
    questionnaire_data['NASA_TLX'] = questionnaire_data[['NASA_1', 'NASA_2', 'NASA_3', 'NASA_4', 'NASA_5', 'NASA_6']].mean(axis=1)

    # Compute stress score as the average of NASA_1 (Mental Demand), NASA_4 (Effort), and NASA_5 (Frustration)
    questionnaire_data['stress_score'] = questionnaire_data[['NASA_1', 'NASA_4', 'NASA_5']].mean(axis=1)

    # Separate data by condition
    haptic_data = questionnaire_data[questionnaire_data['condition'] == 'H']
    mouse_data = questionnaire_data[questionnaire_data['condition'] == 'M']

    # Extract Q2, NASA-TLX, and stress scores
    haptic_q2 = haptic_data['Q2']
    mouse_q2 = mouse_data['Q2']
    haptic_nasa = haptic_data['NASA_TLX']
    mouse_nasa = mouse_data['NASA_TLX']
    haptic_stress = haptic_data['stress_score']
    mouse_stress = mouse_data['stress_score']

    # Perform independent t-tests
    q2_t_stat, q2_p_value = ttest_ind(haptic_q2, mouse_q2, equal_var=False)
    nasa_tlx_t_stat, nasa_tlx_p_value = ttest_ind(haptic_nasa, mouse_nasa, equal_var=False)
    stress_t_stat, stress_p_value = ttest_ind(haptic_stress, mouse_stress, equal_var=False)

    # Return results as a dictionary
    return {
        "Q2": {
            "haptic_mean": haptic_q2.mean(),
            "haptic_std": haptic_q2.std(),
            "mouse_mean": mouse_q2.mean(),
            "mouse_std": mouse_q2.std(),
            "t_stat": q2_t_stat,
            "p_value": q2_p_value
        },
        "NASA_TLX": {
            "haptic_mean": haptic_nasa.mean(),
            "haptic_std": haptic_nasa.std(),
            "mouse_mean": mouse_nasa.mean(),
            "mouse_std": mouse_nasa.std(),
            "t_stat": nasa_tlx_t_stat,
            "p_value": nasa_tlx_p_value
        },
        "stress_score": {
            "haptic_mean": haptic_stress.mean(),
            "haptic_std": haptic_stress.std(),
            "mouse_mean": mouse_stress.mean(),
            "mouse_std": mouse_stress.std(),
            "t_stat": stress_t_stat,
            "p_value": stress_p_value
        }
    }

def analyze_WDQ(questionnaire_data):
    """
    Analyzes WDQ metrics: task autonomy (WDQ_1 and WDQ_2), task significance (WDQ_3 and WDQ_4),
    and task engagement (WDQ_5 and WDQ_6) across conditions (Haptic and Mouse).
    """

    questionnaire_data = questionnaire_data.copy()

    # Combine WDQ_1 and WDQ_2 into a single measure for task autonomy
    questionnaire_data['autonomy_score'] = questionnaire_data[['WDQ_1', 'WDQ_2']].mean(axis=1)

    # Combine WDQ_3 and WDQ_4 into a single measure for task significance
    questionnaire_data['significance_score'] = questionnaire_data[['WDQ_3', 'WDQ_4']].mean(axis=1)

    # Combine WDQ_5 and WDQ_6 into a single measure for task engagement
    questionnaire_data['engagement_score'] = questionnaire_data[['WDQ_5', 'WDQ_6']].mean(axis=1)

    # Separate data by condition
    haptic_data = questionnaire_data[questionnaire_data['condition'] == 'H']
    mouse_data = questionnaire_data[questionnaire_data['condition'] == 'M']

    # Extract scores for each metric
    haptic_autonomy = haptic_data['autonomy_score']
    mouse_autonomy = mouse_data['autonomy_score']

    haptic_significance = haptic_data['significance_score']
    mouse_significance = mouse_data['significance_score']

    haptic_engagement = haptic_data['engagement_score']
    mouse_engagement = mouse_data['engagement_score']

    # Perform independent t-tests for each metric
    autonomy_t_stat, autonomy_p_value = ttest_ind(haptic_autonomy, mouse_autonomy, equal_var=False)
    significance_t_stat, significance_p_value = ttest_ind(haptic_significance, mouse_significance, equal_var=False)
    engagement_t_stat, engagement_p_value = ttest_ind(haptic_engagement, mouse_engagement, equal_var=False)

    # Return results as a dictionary
    return {
        "autonomy_score": {
            "haptic_mean": haptic_autonomy.mean(),
            "haptic_std": haptic_autonomy.std(),
            "mouse_mean": mouse_autonomy.mean(),
            "mouse_std": mouse_autonomy.std(),
            "t_stat": autonomy_t_stat,
            "p_value": autonomy_p_value
        },
        "significance_score": {
            "haptic_mean": haptic_significance.mean(),
            "haptic_std": haptic_significance.std(),
            "mouse_mean": mouse_significance.mean(),
            "mouse_std": mouse_significance.std(),
            "t_stat": significance_t_stat,
            "p_value": significance_p_value
        },
        "engagement_score": {
            "haptic_mean": haptic_engagement.mean(),
            "haptic_std": haptic_engagement.std(),
            "mouse_mean": mouse_engagement.mean(),
            "mouse_std": mouse_engagement.std(),
            "t_stat": engagement_t_stat,
            "p_value": engagement_p_value
        }
    }

def analyze_physical_demand_and_engagement(questionnaire_data):
    """
    Analyzes whether the haptic device leads to higher physical demand and greater task engagement.
    Combines WDQ_5 and WDQ_6 for task engagement and relevant NASA-TLX categories for physical demand.
    """

    questionnaire_data = questionnaire_data.copy()

    # Normalize WDQ (1 to 6) and NASA-TLX (1 to 20) to a common scale (1 to 6)
    nasa_columns = ['NASA_1', 'NASA_2', 'NASA_3', 'NASA_4', 'NASA_5', 'NASA_6']
    for col in nasa_columns:
        questionnaire_data[col + '_normalized'] = (questionnaire_data[col] - 1) * (6 - 1) / (20 - 1) + 1

    # Combine WDQ_5 and WDQ_6 into a single measure for task engagement
    questionnaire_data['engagement_score'] = questionnaire_data[['WDQ_5', 'WDQ_6']].mean(axis=1)

    # Combine normalized NASA-TLX categories into a single measure for physical demand
    questionnaire_data['physical_demand_score'] = questionnaire_data[
        ['NASA_2_normalized', 'NASA_4_normalized', 'NASA_5_normalized']
    ].mean(axis=1)

    # Separate data by condition
    haptic_data = questionnaire_data[questionnaire_data['condition'] == 'H']
    mouse_data = questionnaire_data[questionnaire_data['condition'] == 'M']

    # Extract scores
    haptic_engagement = haptic_data['engagement_score']
    mouse_engagement = mouse_data['engagement_score']
    haptic_physical_demand = haptic_data['physical_demand_score']
    mouse_physical_demand = mouse_data['physical_demand_score']

    # Perform independent t-tests
    engagement_t_stat, engagement_p_value = ttest_ind(haptic_engagement, mouse_engagement, equal_var=False)
    physical_demand_t_stat, physical_demand_p_value = ttest_ind(haptic_physical_demand, mouse_physical_demand, equal_var=False)

    # Return results as a dictionary
    return {
        "engagement_score": {
            "haptic_mean": haptic_engagement.mean(),
            "haptic_std": haptic_engagement.std(),
            "mouse_mean": mouse_engagement.mean(),
            "mouse_std": mouse_engagement.std(),
            "t_stat": engagement_t_stat,
            "p_value": engagement_p_value
        },
        "physical_demand_score": {
            "haptic_mean": haptic_physical_demand.mean(),
            "haptic_std": haptic_physical_demand.std(),
            "mouse_mean": mouse_physical_demand.mean(),
            "mouse_std": mouse_physical_demand.std(),
            "t_stat": physical_demand_t_stat,
            "p_value": physical_demand_p_value
        }
    }
