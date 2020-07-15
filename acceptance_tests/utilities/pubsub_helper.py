import logging

from google.cloud import pubsub_v1
from structlog import wrap_logger

from config import Config

logger = wrap_logger(logging.getLogger(__name__))

subscriber = pubsub_v1.SubscriberClient()


def publish_to_pubsub(message, project, topic, **kwargs):
    publisher = pubsub_v1.PublisherClient()

    topic_path = publisher.topic_path(project, topic)

    future = publisher.publish(topic_path, data=message.encode('utf-8'), **kwargs)

    future.result(timeout=30)
    logger.info("Sent PubSub message", topic=topic, project=project)


def setup_aims_new_address_subscription(context):
    """
    Create a subscriber thread which handles new messages through a callback

    :param subscription_name: The name of the pubsub subscription
    :param subscription_project_id: GCP project where subscription should already exist
    :param callback: The callback to use upon receipt of a new message from the subscription
    :return: a StreamingPullFuture for managing the callback thread
    """
    # subscription_path = client.subscription_path(Config.AIMS_NEW_ADDRESS_PROJECT, Config.AIMS_NEW_ADDRESS_SUBSCRIPTION)
    # subscriber_future = client.subscribe(subscription_path, callback)
    # logger.info('Listening for Pub/Sub Messages', subscription_path=subscription_path)
    # return subscriber_future

    subscription_path = subscriber.subscription_path(Config.AIMS_NEW_ADDRESS_PROJECT,
                                                     Config.AIMS_NEW_ADDRESS_SUBSCRIPTION)
    streaming_pull_future = subscriber.subscribe(subscription_path, callback=aims_callback)
    print("Listening for messages on {}..\n".format(subscription_path))

    with subscriber:
        try:
        except TimeoutError:
            streaming_pull_future.cancel()


def aims_callback(message):
    print("Received message: {}".format(message))
    message.ack()
    # How do we get this to compare the msg to the expected one? without context?
