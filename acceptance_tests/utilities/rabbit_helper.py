import functools
import json
import logging
import os

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
    assert False, "No messages found"
    logger.error('Timed out waiting for messages')
    rabbit.close_connection()


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


RABBIT_AMQP = os.getenv("RABBIT_AMQP", "amqp://guest:guest@localhost:6672")
RABBIT_EXCHANGE = os.getenv("RABBIT_EXCHANGE", "events")
RABBIT_QUEUE = os.getenv("RABBIT_QUEUE", "case.rh.casetest")
RABBIT_ROUTE = os.getenv("RABBIT_ROUTING_KEY", "event.case.*")


def add_queue(rabbitmq_amqp=RABBIT_AMQP,
              binding_key=RABBIT_ROUTE,
              exchange_name=RABBIT_EXCHANGE,
              queue_name=RABBIT_QUEUE):
    """
    Initialise connection to rabbitmq

    :param rabbitmq_amqp: The amqp (url) of the rabbitmq connection
    :param exchange_name: The rabbitmq exchange to publish to, (e.g.: "case-outbound-exchange")
    :param queue_name: The rabbitmq queue that subscribes to the exchange, (e.g.: "Case.Responses")
    :param binding_key: The binding key to associate the exchange and queue (e.g.: "Case.Responses.binding")
    :param queue_args: Arguments passed to the rabbitmq queue declaration
    """
    logger.debug('Connecting to rabbitmq', url=rabbitmq_amqp)
    rabbitmq_connection = pika.BlockingConnection(pika.URLParameters(rabbitmq_amqp))
    channel = rabbitmq_connection.channel()
    channel.exchange_declare(exchange=exchange_name, exchange_type='topic', durable=True)
    channel.queue_declare(queue=queue_name, durable=True)
    channel.queue_bind(exchange=exchange_name, queue=queue_name, routing_key=binding_key)
    logger.info('Successfully initialised rabbitmq', exchange=exchange_name, binding=binding_key)


def add_test_queue(rabbitmq_amqp, binding_key, exchange_name, queue_name):
    """
    Initialise connection to rabbitmq

    :param rabbitmq_amqp: The amqp (url) of the rabbitmq connection
    :param exchange_name: The rabbitmq exchange to publish to, (e.g.: "case-outbound-exchange")
    :param queue_name: The rabbitmq queue that subscribes to the exchange, (e.g.: "Case.Responses")
    :param binding_key: The binding key to associate the exchange and queue (e.g.: "Case.Responses.binding")
    :param queue_args: Arguments passed to the rabbitmq queue declaration
    """
    logger.debug('Connecting to rabbitmq', url=rabbitmq_amqp)
    rabbitmq_connection = pika.BlockingConnection(pika.URLParameters(rabbitmq_amqp))
    channel = rabbitmq_connection.channel()
    channel.exchange_declare(exchange=exchange_name, exchange_type='topic', durable=True)
    channel.queue_declare(queue=queue_name, durable=True)
    channel.queue_bind(exchange=exchange_name, queue=queue_name, routing_key=binding_key)
    logger.info('Successfully initialised rabbitmq', exchange=exchange_name, binding=binding_key)
