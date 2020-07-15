import logging
import time
import uuid
from datetime import datetime

import requests

from acceptance_tests.utilities.rabbit_helper import purge_queues
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


def before_tag(context, tag):
    if tag == "clear_for_bad_messages":
        _clear_queues_for_bad_messages_and_reset_exception_manager()
    if tag == "hardcoded_census_values_for_collection_and_action_plan_ids":
        # For tests where the action plan and collection exercise ID need hardcoding
        # e.g where skeleton cases are used
        context.action_plan_id = Config.CENSUS_ACTION_PLAN_ID
        context.collection_exercise_id = Config.CENSUS_COLLECTION_EXERCISE_ID
    # if tag == 'new_aims_topic_and_subscription':
    #     response = requests.put()
    #         get(f'{Config.CASE_API_CASE_URL}ccs/{case_id}/qid')
    #     test_helper.assertEqual(response.status_code, 200, 'CCS QID API call failed')
    #     response_json = response.json()
    #     return response_json
    #     "http://localhost:8538/v1/projects/project/topics/eq-submission-topic" "PUT" "pubsub_emulator topic"


def after_tag(_, tag):
    if tag == "clear_for_bad_messages":
        _clear_queues_for_bad_messages_and_reset_exception_manager()


def _clear_queues_for_bad_messages_and_reset_exception_manager():
    for _ in range(4):
        purge_queues()
        time.sleep(1)
    time.sleep(5)
    requests.get(f'{Config.EXCEPTION_MANAGER_URL}/reset')
