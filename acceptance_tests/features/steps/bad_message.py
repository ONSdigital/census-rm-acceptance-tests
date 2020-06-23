import hashlib
import json
import time
import uuid

import requests
from behave import then, given

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
