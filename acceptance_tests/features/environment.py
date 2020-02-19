import base64
import json
import time
import uuid
import requests

from datetime import datetime

from acceptance_tests.utilities.rabbit_helper import add_test_queue, purge_queues
from config import Config


def before_all(_context):
    _setup_google_auth()
    add_test_queue(Config.RABBITMQ_CASE_TEST_ROUTE, Config.RABBITMQ_RH_EXCHANGE_NAME,
                   Config.RABBITMQ_RH_OUTBOUND_CASE_QUEUE_TEST)
    add_test_queue(Config.RABBITMQ_UAC_TEST_ROUTE, Config.RABBITMQ_RH_EXCHANGE_NAME,
                   Config.RABBITMQ_RH_OUTBOUND_UAC_QUEUE_TEST)
    add_test_queue("", Config.RABBITMQ_OUTBOUND_ADAPTER_EXCHANGE, Config.RABBITMQ_OUTBOUND_FIELD_QUEUE_TEST,
                   exchange_type='direct')


def after_all(_context):
    purge_queues(Config.RABBITMQ_RH_OUTBOUND_CASE_QUEUE_TEST,
                 Config.RABBITMQ_RH_OUTBOUND_UAC_QUEUE_TEST,
                 Config.RABBITMQ_OUTBOUND_FIELD_QUEUE_TEST)


def before_scenario(context, _):
    context.test_start_local_datetime = datetime.now()
    context.collection_exercise_id = str(uuid.uuid4())
    context.action_plan_id = str(uuid.uuid4())
    context.collection_exercise_id = str(uuid.uuid4())
    purge_queues(Config.RABBITMQ_INBOUND_REFUSAL_QUEUE,
                 Config.RABBITMQ_RH_OUTBOUND_CASE_QUEUE,
                 Config.RABBITMQ_RH_OUTBOUND_UAC_QUEUE,
                 Config.RABBITMQ_RH_OUTBOUND_CASE_QUEUE_TEST,
                 Config.RABBITMQ_RH_OUTBOUND_UAC_QUEUE_TEST,
                 Config.RABBITMQ_SAMPLE_INBOUND_QUEUE,
                 Config.RABBITMQ_UNADDRESSED_REQUEST_QUEUE,
                 Config.RABBITMQ_OUTBOUND_FIELD_QUEUE,
                 Config.RABBITMQ_OUTBOUND_FIELD_QUEUE_TEST,
                 Config.RABBITMQ_INBOUND_FULFILMENT_REQUEST_QUEUE,
                 Config.RABBITMQ_INBOUND_NOTIFY_FULFILMENT_REQUEST_QUEUE)


def before_tag(_, tag):
    if tag == "clear_for_bad_messages":
        _clear_queues_for_bad_messages_and_reset_exception_manager()


def after_tag(_, tag):
    if tag == "clear_for_bad_messages":
        _clear_queues_for_bad_messages_and_reset_exception_manager()


def _clear_queues_for_bad_messages_and_reset_exception_manager():
    for _ in range(0, 4):
        purge_queues(*Config.RABBITMQ_QUEUES, 'delayedRedeliveryQueue', 'RM.Field')
        time.sleep(1)
    time.sleep(5)
    requests.get(f'{Config.EXCEPTION_MANAGER_URL}/reset')


def _setup_google_auth():
    if Config.GOOGLE_SERVICE_ACCOUNT_JSON and Config.GOOGLE_APPLICATION_CREDENTIALS:
        sa_json = json.loads(base64.b64decode(Config.GOOGLE_SERVICE_ACCOUNT_JSON))
        with open(Config.GOOGLE_APPLICATION_CREDENTIALS, 'w') as credentials_file:
            json.dump(sa_json, credentials_file)
        print(f'Created GOOGLE_APPLICATION_CREDENTIALS: {Config.GOOGLE_APPLICATION_CREDENTIALS}')
