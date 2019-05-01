import functools
import logging

import pika
from structlog import wrap_logger

from config import Config

logger = wrap_logger(logging.getLogger(__name__))


def start_listening_to_rabbit_queue(queue, on_message_callback, timeout=30):
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=Config.RABBITMQ_HOST, port=Config.RABBITMQ_PORT))
    channel = connection.channel()
    connection.call_later(delay=timeout, callback=functools.partial(_timeout_callback, channel))
    channel.basic_consume(queue=queue,
                          on_message_callback=on_message_callback)
    channel.start_consuming()


def _timeout_callback(ch):
    logger.error('Timed out waiting for messages')
    ch.stop_consuming()
