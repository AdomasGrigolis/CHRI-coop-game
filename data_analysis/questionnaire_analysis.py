import os
import pandas as pd

def read_questionnaire_data():
    # Questionnaire path
    workspace_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
    data_dir = os.path.join(workspace_dir, "data")
    questionnaire_path = os.path.join(data_dir, 'questionnaires.xlsx')

    # Read the questionnaire data
    questionnaire_data = pd.read_excel(questionnaire_path)
    return questionnaire_data

def calculate_scores(data):
    # Filter data by condition
    conditions = ['H', 'M']
    results = []

    for condition in conditions:
        condition_data = data[data['condition'] == condition]

        # Group by participant_id to handle cases where the same participant is in both conditions
        grouped = condition_data.groupby('participant_id')

        for participant_id, group in grouped:
            q1_value = group['Q1'].values[0]
            q2_value = group['Q2'].values[0]
            # q2 scale is inverted
            q2_value = 6 + 1 - q2_value
            # Calculate NASA score (mean of NASA_1 to NASA_6)
            nasa_columns = ['NASA_1', 'NASA_2', 'NASA_3', 'NASA_4', 'NASA_5', 'NASA_6']
            nasa_score = group[nasa_columns].mean(axis=1).values[0]

            # Calculate WDQ score (mean of WDQ_1 to WDQ_6)
            wdq_columns = ['WDQ_1', 'WDQ_2', 'WDQ_3', 'WDQ_4', 'WDQ_5', 'WDQ_6']
            wdq_score = group[wdq_columns].mean(axis=1).values[0]

            # Calculate WDQ subcategory scores
            wdq_subcategories = {
                'WDQ_sub_1': group[['WDQ_1', 'WDQ_2']].mean(axis=1).values[0],
                'WDQ_sub_2': group[['WDQ_3', 'WDQ_4']].mean(axis=1).values[0],
                'WDQ_sub_3': group[['WDQ_5', 'WDQ_6']].mean(axis=1).values[0],
            }

            # Append results
            results.append({
                'participant_id': participant_id,
                'condition': condition,
                'Q1': q1_value,
                'Q2': q2_value,
                'NASA_score': nasa_score,
                'WDQ_score': wdq_score,
                **wdq_subcategories
            })

    return pd.DataFrame(results)

def calculate_mean_per_condition(scores_df):
    """
    Calculate the mean for all participants per trial (condition) for all categories.
    """
    scores_df = scores_df.drop(columns=['participant_id'])
    mean_per_condition = scores_df.groupby('condition').mean(numeric_only=True).reset_index()

    return mean_per_condition
