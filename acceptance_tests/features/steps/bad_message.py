import hashlib
import json
import random
import time
import requests

from behave import when, then, step

from acceptance_tests.utilities.rabbit_context import RabbitContext
from acceptance_tests.utilities.rabbit_helper import purge_queues
from config import Config


@step('queues are free of messages')
def clear_queues(context):
    purge_queues(*Config.RABBITMQ_QUEUES, 'delayedRedeliveryQueue', 'RM.Field')
    time.sleep(5)
    requests.get(f'{Config.EXCEPTION_MANAGER_URL}/reset')


@when('a bad message is placed on each of the queues')
def publish_bad_message(context):
    message_hashes = []
    for queue in Config.RABBITMQ_QUEUES:
        message = json.dumps(
            {
                "message": "This is a dodgy message",
                "queueName": queue,
                "randomNumber": random.randint(1, 1000)
            }
        )

        with RabbitContext(queue_name=queue) as rabbit:
            rabbit.publish_message(
                message=message,
                content_type='application/json')

        message_hashes.append(hashlib.sha256(message.encode('utf-8')).hexdigest())

    context.message_hashes = message_hashes


@then('the hash of the bad message is seen multiple times')
def check_for_bad_messages(context):
    time.sleep(20)
    response = requests.get(f'{Config.EXCEPTION_MANAGER_URL}/badmessages/summary')
    bad_messages = response.json()

    for bad_message in bad_messages:
        assert bad_message['seenCount'] > 1
        assert bad_message['messageHash'] in context.message_hashes
