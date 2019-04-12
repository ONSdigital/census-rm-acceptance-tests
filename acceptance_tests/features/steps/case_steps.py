import functools
import json
import logging
import time

import pika
from behave import then
from structlog import wrap_logger

from acceptance_tests.controllers.case_controller import get_cases_by_survey_id
from config import Config

logger = wrap_logger(logging.getLogger(__name__))


@then("the sample units are created and stored in the case service")
def check_count_of_cases(context):
    cases = get_cases_by_survey_id(context.survey_id, len(context.sample_units))
    assert len(cases) == len(context.sample_units)


@then("the new cases are emitted to Respondent Home")
def check_messages_are_received(context):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=Config.RABBITMQ_HOST, port=Config.RABBITMQ_PORT))

    channel = connection.channel()

    connection.add_timeout(deadline=30, callback_method=functools.partial(_timeout_callback, channel))

    expected_sample_units = context.sample_units.copy()
    channel.basic_consume(queue=Config.RABBITMQ_RH_OUTBOUND_QUEUE,
                          consumer_callback=functools.partial(_callback, expected_sample_units=expected_sample_units))

    channel.start_consuming()

    if len(expected_sample_units) > 0:
        assert False, 'Some messages are missing'


def _timeout_callback(ch):
    logger.info('Timed out!!!')
    ch.stop_consuming()


def _is_valid_message(parsed_body):
    return _assert_equals(parsed_body['payload']['collectionCase']['survey'], 'Census') \
    and _assert_equals(parsed_body['payload']['collectionCase']['state'], 'ACTIONABLE') \
    and len(parsed_body['payload']['collectionCase']['caseRef']) == 8


def _callback(ch, method, properties, body, expected_sample_units):
    ch.basic_ack(delivery_tag=method.delivery_tag)

    parsed_body = json.loads(body)

    if not _is_valid_message(parsed_body):
        assert False, 'Message body is invalid'

    matched_sample_unit_index = None

    for index, sample_unit in enumerate(expected_sample_units):
        if _sample_matches_rh_message(sample_unit, parsed_body):
            matched_sample_unit_index = index
            break
    if matched_sample_unit_index is None:
        assert False, 'Could not find sample unit'
    del expected_sample_units[matched_sample_unit_index]

    if len(expected_sample_units) == 0:
        ch.stop_consuming()


def _sample_matches_rh_message(sample_unit, rh_message):
    return sample_unit['attributes']['ADDRESS_LINE1'] == rh_message['payload']['collectionCase']['address']['addressLine1'] \
        and sample_unit['attributes']['ADDRESS_LINE2'] == rh_message['payload']['collectionCase']['address']['addressLine2'] \
        and sample_unit['attributes']['RGN'][:1] == rh_message['payload']['collectionCase']['address']['region']


def _assert_equals(expected, actual):
    if expected != actual:
        logger.error(f"Expected {expected}, but got {actual}")
        return False
    return True
