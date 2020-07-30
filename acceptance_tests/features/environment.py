import logging
import time
import uuid
from datetime import datetime

import requests

from acceptance_tests.utilities.pubsub_helper import purge_aims_new_address_topic
from acceptance_tests.utilities.rabbit_helper import purge_queues
from acceptance_tests.utilities.test_case_helper import test_helper
from config import Config


def before_all(_):
    # reduce log level
    logging.getLogger("pika").setLevel(logging.WARNING)


def after_all(_context):
    purge_queues()


def before_scenario(context, _):
    context.test_start_local_datetime = datetime.now()
    context.test_start_utc = datetime.utcnow()

    if not hasattr(context, 'collection_exercise_id'):
        context.collection_exercise_id = str(uuid.uuid4())

    if not hasattr(context, 'action_plan_id'):
        context.action_plan_id = str(uuid.uuid4())

    purge_queues()


def after_scenario(_, scenario):
    if "clear_for_bad_messages" not in scenario.tags:
        response = requests.get(f'{Config.EXCEPTION_MANAGER_URL}/badmessages')
        response.raise_for_status()
        if response.json():
            test_helper.fail('Unexpected exception(s) thrown by RM')


def before_tag(context, tag):
    if tag == "clear_for_bad_messages":
        _clear_queues_for_bad_messages_and_reset_exception_manager()
    if tag == "hardcoded_census_values_for_collection_and_action_plan_ids":
        # For tests where the action plan and collection exercise ID need hardcoding
        # e.g where skeleton cases are used
        context.action_plan_id = Config.CENSUS_ACTION_PLAN_ID
        context.collection_exercise_id = Config.CENSUS_COLLECTION_EXERCISE_ID
    if tag == 'purge_aims_topic':
        purge_aims_new_address_topic()


def after_tag(_, tag):
    if tag == "clear_for_bad_messages":
        _clear_queues_for_bad_messages_and_reset_exception_manager()


def _clear_queues_for_bad_messages_and_reset_exception_manager():
    for _ in range(4):
        purge_queues()
        time.sleep(1)
    time.sleep(5)
    requests.get(f'{Config.EXCEPTION_MANAGER_URL}/reset')
