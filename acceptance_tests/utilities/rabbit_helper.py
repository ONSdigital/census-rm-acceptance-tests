import functools
import json
import logging

import pika
from structlog import wrap_logger

from acceptance_tests.utilities.rabbit_context import (
    RabbitContext
)

logger = wrap_logger(logging.getLogger(__name__))


def start_listening_to_rabbit_queue(queue, on_message_callback, timeout=30):
    rabbit = RabbitContext(queue_name=queue)
    connection = rabbit.open_connection()

    connection.call_later(
        delay=timeout,
        callback=functools.partial(_timeout_callback, rabbit))
    rabbit.channel.basic_consume(
        queue=queue,
        on_message_callback=on_message_callback)
    rabbit.channel.start_consuming()


def _timeout_callback(rabbit):
    logger.error('Timed out waiting for messages')
    rabbit.close_connection()
    assert False, "Didn't find the expected number of messages"


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


def add_test_queue(rabbitmq_amqp, binding_key, exchange_name, queue_name, exchange_type='topic'):
    rabbitmq_connection = pika.BlockingConnection(pika.URLParameters(rabbitmq_amqp))
    channel = rabbitmq_connection.channel()
    channel.exchange_declare(exchange=exchange_name, exchange_type=exchange_type, durable=True)
    channel.queue_declare(queue=queue_name, durable=True)
    channel.queue_bind(exchange=exchange_name, queue=queue_name, routing_key=binding_key)
    logger.info('Successfully add test queue to rabbitmq', exchange=exchange_name, binding=binding_key)
