import logging

from google.cloud import pubsub_v1
from structlog import wrap_logger

logger = wrap_logger(logging.getLogger(__name__))


def publish_to_pubsub(message, project, topic, **kwargs):
    publisher = pubsub_v1.PublisherClient()

    topic_path = publisher.topic_path(project, topic)

    future = publisher.publish(topic_path, data=message.encode('utf-8'), **kwargs)

    future.result(timeout=30)
    logger.info("Sent PubSub message", topic=topic, project=project)
