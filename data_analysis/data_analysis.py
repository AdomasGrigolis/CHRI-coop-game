import questionnaire_analysis
import csv_analysis
import plots
import statistical_tools
import analyse_results
import json

# Parse data
questionnaire_data = questionnaire_analysis.read_questionnaire_data()
scores_df = questionnaire_analysis.calculate_scores(questionnaire_data)
means_df = questionnaire_analysis.calculate_mean_per_condition(scores_df)
csv_data, csv_unfiltered = csv_analysis.combine_data(questionnaire_data)

# Statistical Analysis
completion_time_stats = statistical_tools.analyze_task_completion(csv_data)
learning_curve_stats = statistical_tools.analyze_learning_curve(csv_data)
learning_curve_stats_3_5 = statistical_tools.analyze_learning_curve_tasks_3_to_5(csv_data)
nasa_stress_q2_stats = statistical_tools.analyze_nasa_and_stress(questionnaire_data)
wdq_stats = statistical_tools.analyze_WDQ(questionnaire_data)
physical_demand_and_engagement = statistical_tools.analyze_physical_demand_and_engagement(questionnaire_data)

# Plotting
plots.plot_mean_time(csv_data)
plots.plot_boxplot_conditions(csv_data)
plots.plot_wdq_analysis(wdq_stats)
plots.plot_nasa_metrics(questionnaire_data)

# Print results
print("\nTask Completion Statistics Results:")
print(json.dumps(completion_time_stats, indent=4))
analyse_results.analyse_completion_time(completion_time_stats)
print("\nLearning curve Statistics Results:")
print(json.dumps(learning_curve_stats, indent=4))
analyse_results.analyse_learning_curve(learning_curve_stats)
print("\nLearning curve Statistics Results (Tasks 3 to 5):")
print(json.dumps(learning_curve_stats_3_5, indent=4))
print("\nNASA TLX and Stress Score Statistics Results:")
print(json.dumps(nasa_stress_q2_stats, indent=4))
analyse_results.analyse_stress(nasa_stress_q2_stats)
analyse_results.analyse_grasping_ease(nasa_stress_q2_stats)
print("\nWDQ 1 and 2 Analysis Results:")
print(json.dumps(wdq_stats, indent=4))
analyse_results.analyse_task_engagement(wdq_stats)
analyse_results.analyse_task_autonomy_and_significance(wdq_stats)
print("\nPhysical Demand and Engagement Analysis Results:")
print(json.dumps(physical_demand_and_engagement, indent=4))
analyse_results.analyse_engagement_demand(physical_demand_and_engagement)

