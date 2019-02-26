import logging

import requests
from structlog import wrap_logger

from config import Config

logger = wrap_logger(logging.getLogger(__name__))


def get_action_plans():
    logger.debug('Retrieving action plans')

    url = f'{Config.ACTION_SERVICE}/actionplans'

    response = requests.get(url, auth=Config.BASIC_AUTH)
    response.raise_for_status()

    logger.debug('Successfully retrieved action plans')

    return response.json()
