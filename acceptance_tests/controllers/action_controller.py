import logging

import requests
from structlog import wrap_logger

from config import Config

logger = wrap_logger(logging.getLogger(__name__))


def create_action_plan(action_plan_id):
    logger.info('Creating action plan')

    url = f'{Config.ACTION_SERVICE}/actionPlans'

    body = {'id': action_plan_id}

    response = requests.post(url, auth=Config.BASIC_AUTH, json=body)

    response.raise_for_status()

    logger.info('Successfully created action plan')

    return response.json()


def create_action_type(action_type_id, name, description, handler):
    logger.info('Creating action type')

    url = f'{Config.ACTION_SERVICE}/actionTypes'

    body = {'id': action_type_id, 'name': name, 'description': description, 'handler': handler}

    response = requests.post(url, auth=Config.BASIC_AUTH, json=body)

    response.raise_for_status()

    logger.info('Successfully created action type')

    return response.json()


def create_action_rule(action_rule_id, trigger_date_time, classifiers, action_plan_url, action_type_url,
                       has_triggered=False):
    logger.info('Creating action rule')

    url = f'{Config.ACTION_SERVICE}/actionRules'

    body = {'id': action_rule_id, 'triggerDateTime': trigger_date_time, 'classifiers': classifiers,
            'actionPlan': action_plan_url, 'actionType': action_type_url, 'hasTriggered': has_triggered}

    response = requests.post(url, auth=Config.BASIC_AUTH, json=body)

    response.raise_for_status()

    logger.info('Successfully created action rule')

    return response.json()
