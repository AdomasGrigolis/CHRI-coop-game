import questionnaire_analysis
import csv_analysis
import plots
import statistical_tools
import json

questionnaire_data = questionnaire_analysis.read_questionnaire_data()
scores_df = questionnaire_analysis.calculate_scores(questionnaire_data)
means_df = questionnaire_analysis.calculate_mean_per_condition(scores_df)
csv_data = csv_analysis.combine_data(questionnaire_data)

# Plotting
plots.plot_mean_time(csv_data)
plots.plot_boxplot_conditions(csv_data)

# Statistical Analysis
completion_time_stats = statistical_tools.analyze_task_completion(csv_data)
learning_curve_stats = statistical_tools.analyze_learning_curve(csv_data)

# Print results
print("Task Completion Statistics Results:")
print(json.dumps(completion_time_stats, indent=4))
print("Learning curve Statistics Results:")
print(json.dumps(learning_curve_stats, indent=4))
