import time
import uuid
from datetime import datetime

import requests

from acceptance_tests.utilities.rabbit_helper import purge_queues
from config import Config


# def after_all(_context):
#     purge_queues(Config.RABBITMQ_RH_OUTBOUND_CASE_QUEUE,
#                  Config.RABBITMQ_RH_OUTBOUND_UAC_QUEUE,
#                  Config.RABBITMQ_OUTBOUND_FIELD_QUEUE)


def before_scenario(context, _):
    context.test_start_local_datetime = datetime.now()
    context.collection_exercise_id = str(uuid.uuid4())
    context.action_plan_id = str(uuid.uuid4())
    purge_queues(Config.RABBITMQ_INBOUND_REFUSAL_QUEUE,
                 Config.RABBITMQ_RH_OUTBOUND_CASE_QUEUE,
                 Config.RABBITMQ_RH_OUTBOUND_UAC_QUEUE,
                 Config.RABBITMQ_SAMPLE_INBOUND_QUEUE,
                 Config.RABBITMQ_UNADDRESSED_REQUEST_QUEUE,
                 Config.RABBITMQ_OUTBOUND_FIELD_QUEUE,
                 Config.RABBITMQ_INBOUND_FULFILMENT_REQUEST_QUEUE,
                 Config.RABBITMQ_INBOUND_NOTIFY_FULFILMENT_REQUEST_QUEUE)


def before_tag(_, tag):
    if tag == "clear_for_bad_messages":
        _clear_queues_for_bad_messages_and_reset_exception_manager()


def after_tag(_, tag):
    if tag == "clear_for_bad_messages":
        _clear_queues_for_bad_messages_and_reset_exception_manager()


def _clear_queues_for_bad_messages_and_reset_exception_manager():
    for _ in range(4):
        purge_queues(*Config.RABBITMQ_QUEUES, 'delayedRedeliveryQueue', 'RM.Field')
        time.sleep(1)
    time.sleep(5)
    requests.get(f'{Config.EXCEPTION_MANAGER_URL}/reset')
