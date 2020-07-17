import functools
import json
import logging
from time import sleep

from datetime import datetime
from google.cloud import pubsub_v1
from google.protobuf.timestamp_pb2 import Timestamp

from structlog import wrap_logger

from acceptance_tests.utilities.test_case_helper import test_helper
from config import Config

logger = wrap_logger(logging.getLogger(__name__))

subscriber = pubsub_v1.SubscriberClient()


def publish_to_pubsub(message, project, topic, **kwargs):
    publisher = pubsub_v1.PublisherClient()

    topic_path = publisher.topic_path(project, topic)

    future = publisher.publish(topic_path, data=message.encode('utf-8'), **kwargs)

    future.result(timeout=30)
    logger.info("Sent PubSub message", topic=topic, project=project)


def consume_aims_new_address_messages(context):
    subscription_path = subscriber.subscription_path(Config.AIMS_NEW_ADDRESS_PROJECT,
                                                     Config.AIMS_NEW_ADDRESS_SUBSCRIPTION)
    subscriber.subscribe(subscription_path, callback=functools.partial(store_aims_new_address_message, context=context))


def store_aims_new_address_message(message, context):
    context.aims_new_address_message = json.loads(message.data)
    message.ack()


def sync_consume_of_pubsub(context):
    subscription_path = subscriber.subscription_path(Config.AIMS_NEW_ADDRESS_PROJECT,
                                                     Config.AIMS_NEW_ADDRESS_SUBSCRIPTION)

    response = subscriber.pull(subscription_path, max_messages=2, timeout=5)
    test_helper.assertEqual(len(response.received_messages), 1)

    context.aims_new_address_message = json.loads(response.received_messages[0].message.data)

    ack_ids = []
    for received_message in response.received_messages:
        ack_ids.append(received_message.ack_id)

    subscriber.acknowledge(subscription_path, ack_ids)


def purge_aims_new_address_topic():
    subscription_path = subscriber.subscription_path(Config.AIMS_NEW_ADDRESS_PROJECT,
                                                     Config.AIMS_NEW_ADDRESS_SUBSCRIPTION)
    response = subscriber.pull(subscription_path, max_messages=100, timeout=1)

    ack_ids = []
    for received_message in response.received_messages:
        ack_ids.append(received_message.ack_id)

    if len(ack_ids) > 0:
        subscriber.acknowledge(subscription_path, ack_ids)

    if len(response.received_messages) == 100:
        purge_aims_new_address_topic()
