import os
import pandas as pd

def combine_data(questionnaire_data):
    """
    Combines questionnaire data with trial, success rate, and time data.
    Filters out rows with extreme outliers in the 'time' column and rows where 'time' is 0.
    Each row in questionnaire_data corresponds to 5 trials.
    Only 'participant_id' and 'condition' columns are used from questionnaire_data.
    """

    # Define file paths
    workspace_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
    data_dir = os.path.join(workspace_dir, "data")

    trials_path = os.path.join(data_dir, 'trials.csv')
    success_rate_path = os.path.join(data_dir, 'success_rate.csv')
    times_path = os.path.join(data_dir, 'times.csv')

    # Drop unnecessary columns from questionnaire_data
    questionnaire_data = questionnaire_data[['participant_id', 'condition']].copy()

    # Load the trial-related data
    trials_df = pd.read_csv(trials_path, header=None, names=['trial_number'])
    success_rate_df = pd.read_csv(success_rate_path, header=None, names=['success_rate'])
    times_df = pd.read_csv(times_path, header=None, names=['time'])

    # Combine the trial-related data
    combined_trials_df = pd.concat([trials_df, success_rate_df, times_df], axis=1)

    # Repeat each row in questionnaire_data 5 times to match the trial data
    repeated_questionnaire_data = questionnaire_data.loc[
        questionnaire_data.index.repeat(5)
    ].reset_index(drop=True)

    # Concatenate the repeated questionnaire data with the trial-related data
    final_df = pd.concat([repeated_questionnaire_data, combined_trials_df], axis=1)

    # Drop rows with missing values
    final_df = final_df.dropna()

    final_df_unfiltered = final_df.copy()

    # Drop rows where 'time' is 0
    final_df = final_df[final_df['time'] != 0]

    # Filter out extreme outliers in the 'time' column using the IQR method
    Q1 = final_df['time'].quantile(0.25)  # First quartile (25th percentile)
    Q3 = final_df['time'].quantile(0.75)  # Third quartile (75th percentile)
    IQR = Q3 - Q1  # Interquartile range
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    final_df = final_df[(final_df['time'] >= lower_bound) & (final_df['time'] <= upper_bound)]

    # Ensure 'participant_id' is an integer
    final_df['participant_id'] = final_df['participant_id'].astype(int)

    # Print the number of participants loaded
    num_participants = final_df['participant_id'].nunique()
    print(f"Number of participants loaded successfully: {num_participants}")

    return final_df, final_df_unfiltered