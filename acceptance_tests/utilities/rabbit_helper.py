import functools
import json
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


def store_all_msgs_in_context(ch, method, _properties, body, context, expected_msg_count, type_filter=None):
    parsed_body = json.loads(body)

    if parsed_body['event']['type'] == type_filter or type_filter is None:
        context.messages_received.append(parsed_body)
        ch.basic_ack(delivery_tag=method.delivery_tag)
    else:
        # take it, ignore it?
        ch.basic_nack(delivery_tag=method.delivery_tag)

    if len(context.messages_received) == expected_msg_count:
        ch.stop_consuming()


def _timeout_callback(ch):
    logger.error('Timed out waiting for messages')
    ch.stop_consuming()
