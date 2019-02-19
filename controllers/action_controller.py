import logging

import requests
from structlog import wrap_logger

from config import Config
from utilities.date_utilities import convert_to_iso_timestamp

logger = wrap_logger(logging.getLogger(__name__))


def create_action_plan(survey_ref, collection_exercise_id, action_type):
    logger.info('Creating action plan', survey_ref=survey_ref, collection_exercise_id=collection_exercise_id,
                action_type=action_type)

    try:
        trigger_date_time = convert_to_iso_timestamp('2019-02-11T11:11')
    except ValueError:
        return -1

    action_plan_name = survey_ref + ' H 1'
    action_plans = get_action_plans()
    collex_action_plans = [plan for plan in action_plans
                           if _plan_for_collection_exercise(plan, collection_exercise_id)]

    action_plan_data = _build_combined_action_data(collex_action_plans)
    action_plan_id = action_plan_data[0]['id']

    rule = {
        'actionPlanId': action_plan_id,
        'actionTypeName': action_type,
        'name': action_plan_name,
        'description': 'myActionPlanDesc',
        'triggerDateTime': trigger_date_time,
        'priority': 3
    }

    url = f'{Config.ACTION_SERVICE}/actionrules'

    response = requests.post(url, auth=Config.BASIC_AUTH, json=rule)
    response.raise_for_status()

    logger.info('Successfully created action plan', survey_ref=survey_ref,
                collection_exercise_id=collection_exercise_id, action_type=action_type)

    return response, action_plan_id


def get_action_plans():
    logger.info('Retrieving action plan')

    url = f'{Config.ACTION_SERVICE}/actionplans'

    action_plans_response = requests.get(url, auth=Config.BASIC_AUTH)
    action_plans_response.raise_for_status()

    logger.info('Successfully retrieved action plan')

    return action_plans_response.json()


def get_action_rules(action_plan_id):
    logger.info('Retrieving action rules', action_plan_id=action_plan_id)

    url = f'{Config.ACTION_SERVICE}/actionrules/actionplan/{action_plan_id}'

    response = requests.get(url, auth=Config.BASIC_AUTH)
    response.raise_for_status()

    logger.info('Successfully retrieved action rules', action_plan_id=action_plan_id)

    return response.json()


def _plan_for_collection_exercise(plan, collection_exercise_id):
    if not plan['selectors']:
        return False
    return plan['selectors']['collectionExerciseId'] == collection_exercise_id


def _build_combined_action_data(action_plans):
    action_data = []
    for action_plan in action_plans:
        action_rule_id = action_plan.get('id')
        action_rules = get_action_rules(action_rule_id)
        action_rules = sorted(action_rules, key=lambda k: k['triggerDateTime'])
        action_plan['action_rules'] = action_rules
        action_data.append(action_plan)
    return action_data
