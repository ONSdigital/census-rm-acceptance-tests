import acceptance_tests.controllers.action_controller as action_controller
from acceptance_tests.utilities.date_utilities import convert_datetime_to_str


def create_action_rule(survey_ref, action_rule_name, action_type_name, trigger_date, action_plan_id):
    rule = {
        'actionPlanId': action_plan_id,
        'actionTypeName': action_type_name,
        'name': action_rule_name,
        'description': survey_ref,
        'triggerDateTime': convert_datetime_to_str(trigger_date),
        'priority': 3
    }

    action_controller.create_action_rule(rule)


def get_id_of_1st_action_plan_for_collection_excercise(collection_exercise_id):
    action_plans = action_controller.get_action_plans()

    for action_plan in action_plans:
        if _plan_for_collection_exercise(action_plan, collection_exercise_id):
            return action_plan.get('id')

    assert False, f'No Action Plan ID found for collection_exercise_id: {collection_exercise_id}'


def _plan_for_collection_exercise(plan, collection_exercise_id):
    if not plan['selectors']:
        return False

    return plan['selectors']['collectionExerciseId'] == collection_exercise_id
