import logging

import requests
from structlog import wrap_logger

from config import Config

logger = wrap_logger(logging.getLogger(__name__))


def create_action_rule(rule):
    logger.info('Creating action rule')

    url = f'{Config.ACTION_SERVICE}/actionrules'

    response = requests.post(url, auth=Config.BASIC_AUTH, json=rule)

    response.raise_for_status()

    logger.info('Successfully created action rule')

    return response.json()


def get_action_plans():
    logger.info('Retrieving action plans')

    url = f'{Config.ACTION_SERVICE}/actionplans'

    response = requests.get(url, auth=Config.BASIC_AUTH)
    response.raise_for_status()

    logger.info('Successfully retrieved action plans')

    return response.json()


def get_action_rules(action_plan_id):
    logger.info('Retrieving action rules')

    url = f'{Config.ACTION_SERVICE}/actionrules/actionplan/{action_plan_id}'

    response = requests.get(url, auth=Config.BASIC_AUTH)
    response.raise_for_status()

    logger.info('Successfully retrieved action rules')

    return response.json()
