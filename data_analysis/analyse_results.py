p_value_threshold = 0.10

def analyse_completion_time(completion_time_stats):
    haptic_mean = completion_time_stats['haptic_mean']
    mouse_mean = completion_time_stats['mouse_mean']
    p_value = completion_time_stats['p_value']

    if p_value < p_value_threshold:
        if haptic_mean < mouse_mean:
            print("  Interpretation: Task completion is significantly faster with the haptic device compared to the mouse.")
        else:
            print("  Interpretation: Task completion is significantly faster with the mouse compared to the haptic device.")
    else:
        print("  Interpretation: There is no significant difference in task completion time between the haptic device and the mouse.")

def analyse_learning_curve(learning_curve_stats):
    haptic_slope = learning_curve_stats['haptic_slope']
    mouse_slope = learning_curve_stats['mouse_slope']

    if haptic_slope < 0 and mouse_slope < 0:
        if haptic_slope < mouse_slope:  # More negative slope indicates faster improvement
            print("  Interpretation: The haptic device shows a steeper learning curve, indicating faster improvement over trials.")
        else:
            print("  Interpretation: The mouse shows a steeper learning curve, indicating faster improvement over trials.")
    elif haptic_slope < 0:
        print("  Interpretation: The haptic device shows a learning curve, while the mouse does not.")
    elif mouse_slope < 0:
        print("  Interpretation: The mouse shows a learning curve, while the haptic device does not.")
    else:
        print("  Interpretation: Neither the haptic device nor the mouse shows a significant learning curve.")

def analyse_engagement_demand(physical_demand_and_engagement):
    engagement_p_value = physical_demand_and_engagement['engagement_score']['p_value']
    physical_demand_p_value = physical_demand_and_engagement['physical_demand_score']['p_value']
    haptic_engagement_mean = physical_demand_and_engagement['engagement_score']['haptic_mean']
    mouse_engagement_mean = physical_demand_and_engagement['engagement_score']['mouse_mean']
    haptic_physical_demand = physical_demand_and_engagement['physical_demand_score']['haptic_mean']
    mouse_physical_demand = physical_demand_and_engagement['physical_demand_score']['mouse_mean']
    if engagement_p_value < p_value_threshold:
        if haptic_engagement_mean > mouse_engagement_mean:
            print("  Interpretation: The haptic device leads to significantly greater task engagement compared to the mouse.")
        else:
            print("  Interpretation: The mouse leads to significantly greater task engagement compared to the haptic device.")
    else:
        print("  Interpretation: There is no significant difference in task engagement between the haptic device and the mouse.")

    if physical_demand_p_value < p_value_threshold:
        if haptic_physical_demand > mouse_physical_demand:
            print("  Interpretation: The haptic device leads to significantly higher physical demand compared to the mouse.")
        else:
            print("  Interpretation: The mouse leads to significantly higher physical demand compared to the haptic device.")
    else:
        print("  Interpretation: There is no significant difference in physical demand between the haptic device and the mouse.")

def analyse_grasping_ease(nasa_stress_q2_stats):
    q2_p_value = nasa_stress_q2_stats['Q2']['p_value']
    haptic_q2_mean = nasa_stress_q2_stats['Q2']['haptic_mean']
    mouse_q2_mean = nasa_stress_q2_stats['Q2']['mouse_mean']
    if q2_p_value < p_value_threshold:
        if haptic_q2_mean > mouse_q2_mean:
            print("  Interpretation: It is significantly easier for participants to grasp objects using the haptic interface.")
        else:
            print("  Interpretation: It is significantly easier for participants to grasp objects using the mouse.")
    else:
        print("  Interpretation: There is no significant difference in ease of grasping between the haptic interface and the mouse.")

def analyse_task_engagement(wdq_stats):
    """
    Analyzes task engagement based on WDQ metrics.
    """

    engagement_p_value = wdq_stats['engagement_score']['p_value']
    haptic_engagement_mean = wdq_stats['engagement_score']['haptic_mean']
    mouse_engagement_mean = wdq_stats['engagement_score']['mouse_mean']
    if engagement_p_value < p_value_threshold:
        if haptic_engagement_mean > mouse_engagement_mean:
            print("  Interpretation: The haptic device leads to significantly higher task engagement compared to the mouse.")
        else:
            print("  Interpretation: The mouse leads to significantly higher task engagement compared to the haptic device.")
    else:
        print("  Interpretation: There is no significant difference in task engagement between the haptic device and the mouse.")

def analyse_stress(nasa_stress_q2_stats):
    stress_p_value = nasa_stress_q2_stats['stress_score']['p_value']
    haptic_stress_mean = nasa_stress_q2_stats['stress_score']['haptic_mean']
    mouse_stress_mean = nasa_stress_q2_stats['stress_score']['mouse_mean']
    if stress_p_value < p_value_threshold:
        if haptic_stress_mean > mouse_stress_mean:
            print("  Interpretation: Participants feel significantly higher stress with the haptic device.")
        else:
            print("  Interpretation: Participants feel significantly higher stress with the mouse.")
    else:
        print("  Interpretation: There is no significant difference in stress levels between the haptic device and the mouse.")

def analyse_task_autonomy_and_significance(wdq_stats):
    """
    Analyzes task autonomy and task significance based on WDQ metrics.
    """

    # Task Autonomy Analysis
    autonomy_p_value = wdq_stats['autonomy_score']['p_value']
    haptic_autonomy_mean = wdq_stats['autonomy_score']['haptic_mean']
    mouse_autonomy_mean = wdq_stats['autonomy_score']['mouse_mean']
    if autonomy_p_value < p_value_threshold:
        if haptic_autonomy_mean > mouse_autonomy_mean:
            print("  Interpretation: The haptic device scores significantly higher on task autonomy compared to the mouse.")
        else:
            print("  Interpretation: The mouse scores significantly higher on task autonomy compared to the haptic device.")
    else:
        print("  Interpretation: There is no significant difference in task autonomy between the haptic device and the mouse.")

    # Task Significance Analysis
    significance_p_value = wdq_stats['significance_score']['p_value']
    haptic_significance_mean = wdq_stats['significance_score']['haptic_mean']
    mouse_significance_mean = wdq_stats['significance_score']['mouse_mean']
    if significance_p_value < p_value_threshold:
        if haptic_significance_mean > mouse_significance_mean:
            print("  Interpretation: The haptic device scores significantly higher on task significance compared to the mouse.")
        else:
            print("  Interpretation: The mouse scores significantly higher on task significance compared to the haptic device.")
    else:
        print("  Interpretation: There is no significant difference in task significance between the haptic device and the mouse.")