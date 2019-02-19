from controllers.action_controller import get_action_rules, create_action_plan, get_action_plans


def setup_action_plan(survey_ref, collection_exercise_id, action_type):
    return create_action_plan(survey_ref, collection_exercise_id, action_type)


def setup_action_plans():
    return get_action_plans()


def setup_action_rules(action_plan_id):
    return get_action_rules(action_plan_id)
