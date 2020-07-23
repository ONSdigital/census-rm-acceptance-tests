import hashlib
import json
import time
import urllib
import uuid

import requests
from behave import given
from behave.step_registry import then
from requests.auth import HTTPBasicAuth

from acceptance_tests.utilities.rabbit_context import RabbitContext
from acceptance_tests.utilities.test_case_helper import test_helper
from config import Config


@given('a bad message is placed on each of the queues')
def publish_bad_message(context):
    message_hashes = []
    for queue in Config.RABBITMQ_QUEUES_WITH_DLQS:
        message = json.dumps(
            {
                "message": "This is a dodgy message",
                "queueName": queue,
                "uniqueness": str(uuid.uuid4())
            }
        )

        with RabbitContext(queue_name=queue) as rabbit:
            rabbit.publish_message(
                message=message,
                content_type='application/json')

        message_hashes.append(hashlib.sha256(message.encode('utf-8')).hexdigest())

    context.message_hashes = message_hashes


@then("each bad message is seen multiple times by the exception manager")
def check_for_bad_messages(context):
    time.sleep(30)
    response = requests.get(f'{Config.EXCEPTION_MANAGER_URL}/badmessages/summary')
    bad_messages = response.json()

    for bad_message in bad_messages:
        test_helper.assertGreater(bad_message['seenCount'], 1,
                                  msg=f'Seen count is not greater than 1, failed bad message summary: {bad_message}')
        test_helper.assertIn(bad_message['messageHash'], context.message_hashes,
                             msg=f'Unknown bad message hash, message summary: {bad_message}')


@then("message redelivery does not go bananas")
def check_message_redelivery_rate(context):
    time.sleep(2)  # Wait a couple of seconds for all hell to break loose

    v_host = urllib.parse.quote(Config.RABBITMQ_VHOST, safe='')
    response = requests.get(
        f'http://{Config.RABBITMQ_HOST}:{Config.RABBITMQ_HTTP_PORT}/api/queues/{v_host}/Case.Responses',
        auth=HTTPBasicAuth(Config.RABBITMQ_USER, Config.RABBITMQ_PASSWORD))

    response.raise_for_status()
    queue_details = response.json()
    redeliver_rate = queue_details.get('message_stats', {}).get('redeliver_details', {}).get('rate')
    test_helper.assertFalse(redeliver_rate, "Redeliver rate should be zero")

    response = requests.get(
        f'http://{Config.RABBITMQ_HOST}:{Config.RABBITMQ_HTTP_PORT}/api/queues/{v_host}/FieldworkAdapter.caseUpdated',
        auth=HTTPBasicAuth(Config.RABBITMQ_USER, Config.RABBITMQ_PASSWORD))

    response.raise_for_status()
    queue_details = response.json()
    redeliver_rate = queue_details.get('message_stats', {}).get('redeliver_details', {}).get('rate')

    test_helper.assertFalse(redeliver_rate, "Redeliver rate should be zero")
