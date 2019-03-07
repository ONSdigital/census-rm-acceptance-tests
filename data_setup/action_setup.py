from datetime import datetime

from controllers.action_controller import get_action_plans, get_action_rules, create_action_rule


def create_action_plan(survey_ref, collection_exercise_id):
    try:
        trigger_date_time = get_actionplan_datetime()
    except ValueError:
        return -1

    action_plan_name = survey_ref + ' H 1'
    action_plans = get_action_plans()
    collex_action_plans = [plan for plan in action_plans
                           if plan_for_collection_exercise(plan, collection_exercise_id)]

    action_plan_data = build_combined_action_data(collex_action_plans)
    action_plan_id = action_plan_data[0]['id']

    rule = {
        'actionPlanId': action_plan_id,
        'actionTypeName': 'SOCIALNOT',
        'name': action_plan_name,
        'description': 'myActionPlanDesc',
        'triggerDateTime': trigger_date_time,
        'priority': 3
    }

    create_action_rule(rule)

    return action_plan_id


def plan_for_collection_exercise(plan, collection_exercise_id):
    if not plan['selectors']:
        return False
    return plan['selectors']['collectionExerciseId'] == collection_exercise_id


def build_combined_action_data(action_plans):
    action_data = []
    for action_plan in action_plans:
        action_rule_id = action_plan.get('id')
        action_rules = get_action_rules(action_rule_id)
        action_rules = sorted(action_rules, key=lambda k: k['triggerDateTime'])
        action_plan['action_rules'] = action_rules
        action_data.append(action_plan)
    return action_data


def get_actionplan_datetime():
    now = datetime.utcnow()
    base_date = datetime(now.year, now.month, now.day, now.hour, now.minute, now.second, now.microsecond)
    return datetime.strftime(base_date, '%Y-%m-%dT%H:%M:%S.000Z')


def get_action_plan_id(collection_exercise_id):
    action_plans = get_action_plans()
    for plan in action_plans:
        if _plan_for_collection_exercise(plan, collection_exercise_id):
            return plan['id']
    assert False, f'No Action Plan ID found for collection_exercise_id: {collection_exercise_id}'


def _plan_for_collection_exercise(plan, collection_exercise_id):
    if not plan['selectors']:
        return False
    return plan['selectors']['collectionExerciseId'] == collection_exercise_id
