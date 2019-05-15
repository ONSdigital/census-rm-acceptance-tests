import functools
import json
import time

from behave import when, then
from coverage.python import os
from google.cloud import pubsub_v1

from acceptance_tests.utilities.rabbit_helper import start_listening_to_rabbit_queue
from config import Config

RECEIPT_TOPIC_PROJECT_ID = "project"
RECEIPT_TOPIC_NAME = "eq-submission-topic"


@when("the receipt msg for the created case is put on the GCP pubsub")
def receipt_msg_published_to_gcp_pubsub(context):
    # get the case id from the case created events
    context.createdCases = []
    _get_emited_msgs(context, _case_created_msg_capture)
    case = context.createdCases[0]

    case_arid = case['address']['arid']
    expected_arid = context.sample_units[0]['attributes']['ARID']

    assert case_arid == expected_arid

    _publish_to_pubsub(case_id=case['id'])


@then("a uac_updated msg is emitted with active set to false")
def uac_updated_msg_emitted(context):
    start_listening_to_rabbit_queue(Config.RABBITMQ_RH_OUTBOUND_QUEUE,
                                    functools.partial(uac_updated_capture, context=context))


def uac_updated_capture(ch, method, _properties, body, context):
    parsed_body = json.loads(body)

    if parsed_body['event']['type'] == 'UAC_UPDATED':
        uac = parsed_body['payload']['uac']
        assert context.createdCases[0]['id'] == uac['caseId']
        assert uac['active'] is False
        ch.basic_nack(delivery_tag=method.delivery_tag)
        ch.stop_consuming()


def _get_emited_msgs(context, callback):
    context.messages_received = []
    start_listening_to_rabbit_queue(Config.RABBITMQ_RH_OUTBOUND_QUEUE, functools.partial(callback, context=context))


def _case_created_msg_capture(ch, method, _properties, body, context):
    parsed_body = json.loads(body)

    if parsed_body['event']['type'] == 'CASE_CREATED':
        created_case = parsed_body['payload']['collectionCase']
        context.createdCases.append(created_case)
        ch.basic_nack(delivery_tag=method.delivery_tag)
        ch.stop_consuming()

        return


def _publish_to_pubsub(case_id, tx_id="0", questionnaire_id="0"):
    os.environ["PUBSUB_EMULATOR_HOST"] = "localhost:8538"
    publisher = pubsub_v1.PublisherClient()

    topic_path = publisher.topic_path(RECEIPT_TOPIC_PROJECT_ID, RECEIPT_TOPIC_NAME)

    data = json.dumps({
        "timeCreated": "2008-08-24T00:00:00Z",
        "metadata": {
            "case_id": case_id,
            "tx_id": tx_id,
            "questionnaire_id": questionnaire_id,
        }
    })

    future = publisher.publish(topic_path,
                               data=data.encode('utf-8'),
                               eventType='OBJECT_FINALIZE',
                               bucketId='123',
                               objectId=tx_id)
    while not future.done():
        time.sleep(1)

    print(f'Message published to {topic_path}')
