from datetime import datetime, timedelta
import requests
from behave import given

from config import Config
from data_setup.action_setup import get_action_plan_id
from data_setup.collection_exercise_setup import setup_census_collection_exercise_to_scheduled_state
from data_setup.survey_setup import setup_census_survey


@given('a survey exists with a collection exercise')
def a_survey_exists_with_collex(context):
    setup_census_survey(context)
    setup_census_collection_exercise_to_scheduled_state(context)

    action_response, context.action_plan_id = create_action_plan(context.survey_ref, context.collection_exercise_id)

    assert action_response.status_code == requests.codes.created
    # context.action_plan_id = get_action_plan_id(context.collection_exercise_id)


def create_action_plan(survey_ref, collection_exercise_id):
    try:
        dt = convert_to_iso_timestamp()
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
        'triggerDateTime': dt,
        'priority': 3
    }

    action_rules_response = requests.post(f'{Config.ACTION_SERVICE}/actionrules', auth=Config.BASIC_AUTH, json=rule)

    return action_rules_response, action_plan_id

def get_action_plans():
    action_plans_response = requests.get(f'{Config.ACTION_SERVICE}/actionplans', auth=Config.BASIC_AUTH)
    action_plans_response.raise_for_status()
    return action_plans_response.json()


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


def get_action_rules(action_plan_id):
    response = requests.get(f'{Config.ACTION_SERVICE}/actionrules/actionplan/{action_plan_id}', auth=Config.BASIC_AUTH)
    response.raise_for_status()
    return response.json()


def convert_to_iso_timestamp():
    now = datetime.utcnow()

    base_date = datetime(now.year, now.month, now.day, now.hour, now.minute, now.second + 5, now.microsecond)

    return datetime.strftime(base_date, '%Y-%m-%dT%H:%M:%S.000Z')

    # return base_date.isoformat()

    # timestamp = datetime.strptime(timestamp_string, "%Y-%m-%dT%H:%M")
    # timestamp_iso = timestamp.astimezone(tzlocal.get_localzone()).isoformat(timespec='milliseconds')
    # return timestamp_iso