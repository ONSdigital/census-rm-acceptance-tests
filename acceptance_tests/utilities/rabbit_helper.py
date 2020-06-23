import functools
import json
import logging

import requests
from structlog import wrap_logger

from acceptance_tests.utilities.rabbit_context import RabbitContext
from acceptance_tests.utilities.test_case_helper import test_helper
from config import Config

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
    test_helper.fail("Didn't find the expected number of messages")


def store_all_msgs_in_context(ch, method, _properties, body, context, expected_msg_count, type_filter=None):
    parsed_body = json.loads(body)

    if type_filter is None or parsed_body['event']['type'] == type_filter:
        context.messages_received.append(parsed_body)
        ch.basic_ack(delivery_tag=method.delivery_tag)
    else:
        # take it, ignore it?
        ch.basic_nack(delivery_tag=method.delivery_tag)

    if len(context.messages_received) == expected_msg_count:
        ch.stop_consuming()


def store_all_case_created_msgs_by_collection_exercise_id(ch, method, _properties, body, context, expected_msg_count,
                                                          collection_exercise_id):
    parsed_body = json.loads(body)

    if (parsed_body['event']['type'] == 'CASE_CREATED' and
            parsed_body['payload']['collectionCase']['collectionExerciseId'] == collection_exercise_id):
        context.messages_received.append(parsed_body)
        ch.basic_ack(delivery_tag=method.delivery_tag)
    else:
        # take it, ignore it?
        ch.basic_nack(delivery_tag=method.delivery_tag)

    if len(context.messages_received) == expected_msg_count:
        ch.stop_consuming()


def store_all_uac_updated_msgs_by_collection_exercise_id(ch, method, _properties, body, context, expected_msg_count,
                                                         collection_exercise_id):
    parsed_body = json.loads(body)

    if (parsed_body['event']['type'] == 'UAC_UPDATED' and
            parsed_body['payload']['uac']['collectionExerciseId'] == collection_exercise_id):
        context.messages_received.append(parsed_body)
        ch.basic_ack(delivery_tag=method.delivery_tag)
    else:
        # take it, ignore it?

        ch.basic_nack(delivery_tag=method.delivery_tag)

    if len(context.messages_received) == expected_msg_count:
        ch.stop_consuming()


def store_first_message_in_context(ch, method, _properties, body, context, type_filter=None):
    parsed_body = json.loads(body)
    if parsed_body['event']['type'] == type_filter or type_filter is None:
        context.first_message = parsed_body
        ch.basic_ack(delivery_tag=method.delivery_tag)
        ch.stop_consuming()
    else:
        ch.basic_nack(delivery_tag=method.delivery_tag)


def purge_queues():
    all_queues = _get_all_queues()
    with RabbitContext() as rabbit:
        for queue in all_queues:
            rabbit.channel.queue_purge(queue=queue)


def check_no_msgs_sent_to_queue(context, queue, on_message_callback, timeout=5):
    context.messages_received = []
    rabbit = RabbitContext(queue_name=queue)
    connection = rabbit.open_connection()

    connection.call_later(
        delay=timeout,
        callback=functools.partial(_timeout_callback_expected, rabbit))

    rabbit.channel.basic_consume(
        queue=queue,
        on_message_callback=on_message_callback)
    rabbit.channel.start_consuming()
    if len(context.messages_received) > 0:
        test_helper.fail(f'Expected no messages on the queue {queue}, found {len(context.messages_received)}'
                         f', message(s): {context.messages_received}')


def _timeout_callback_expected(rabbit):
    rabbit.close_connection()


def _get_all_queues():
    uri = f'http://{Config.RABBITMQ_HOST}:{Config.RABBITMQ_HTTP_PORT}/api/queues/%2f/'
    response = requests.get(uri, auth=(Config.RABBITMQ_USER, Config.RABBITMQ_PASSWORD))
    response.raise_for_status()
    response_data = json.loads(response.content)

    return [queue['name'] for queue in response_data]
