from controllers.action_controller import get_action_plans, create_action_rule
from utilities.date_utilities import get_datetime_now_as_str


def create_action_plan(survey_ref, collection_exercise_id, action_rule_name, action_type_name):
    trigger_date_time = get_datetime_now_as_str()
    action_plan_id = _get_id_of_1st_action_plan_for_collection_excercise(collection_exercise_id)

    rule = {
        'actionPlanId': action_plan_id,
        'actionTypeName': action_type_name,
        'name': action_rule_name,
        'description': survey_ref,
        'triggerDateTime': trigger_date_time,
        'priority': 3
    }

    create_action_rule(rule)

    return action_plan_id


def _get_id_of_1st_action_plan_for_collection_excercise(collection_exercise_id):
    action_plans = get_action_plans()

    for action_plan in action_plans:
        if _plan_for_collection_exercise(action_plan, collection_exercise_id):
            return action_plan.get('id')

    assert False, f'No Action Plan ID found for collection_exercise_id: {collection_exercise_id}'


def _plan_for_collection_exercise(plan, collection_exercise_id):
    if not plan['selectors']:
        return False

    return plan['selectors']['collectionExerciseId'] == collection_exercise_id
