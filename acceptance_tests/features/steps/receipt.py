import functools
import json
import time
from datetime import datetime

from behave import when, step, then
from google.api_core.exceptions import GoogleAPIError
from google.cloud import pubsub_v1

from acceptance_tests.utilities.date_utilities import convert_datetime_to_str
from rabbit_context import RabbitContext
from acceptance_tests.utilities.rabbit_helper import start_listening_to_rabbit_queue, store_all_msgs_in_context
from config import Config


@when("the receipt msg for the created case is put on the GCP pubsub")
def receipt_msg_published_to_gcp_pubsub(context):
    context.emitted_case = context.case_created_events[0]['payload']['collectionCase']
    _publish_object_finalize(context, case_id=context.emitted_case['id'])
    assert context.sent_to_gcp is True


@then("a uac_updated msg is emitted with active set to false")
def uac_updated_msg_emitted(context):
    context.messages_received = []
    start_listening_to_rabbit_queue(Config.RABBITMQ_RH_OUTBOUND_UAC_QUEUE_TEST,
                                    functools.partial(
                                        store_all_msgs_in_context, context=context,
                                        expected_msg_count=1,
                                        type_filter='UAC_UPDATED'))

    assert len(context.messages_received) == 1
    uac = context.messages_received[0]['payload']['uac']
    assert uac['caseId'] == context.emitted_case['id']
    assert uac['active'] is False


@step("a case receipt notification is received")
def create_receipt_received_message_from_eq(context):
    # First case in list will be receipted
    context.receipted_case_id = context.case_created_events[0]['payload']['collectionCase']['id']

    with RabbitContext(queue_name=Config.RABBITMQ_INBOUND_EQ_QUEUE) as rabbit:
        rabbit.publish_message(
            message=_create_receipt_received_json(context.receipted_case_id),
            content_type='application/json')


def _publish_object_finalize(context, case_id="0", tx_id="0", questionnaire_id="0"):
    context.sent_to_gcp = False

    publisher = pubsub_v1.PublisherClient()

    topic_path = publisher.topic_path(Config.RECEIPT_TOPIC_PROJECT, Config.RECEIPT_TOPIC_ID)

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
                               bucketId='eq-bucket',
                               objectId=tx_id)
    if not future.done():
        time.sleep(1)
    try:
        future.result(timeout=30)
    except GoogleAPIError:
        return

    print(f'Message published to {topic_path}')

    context.sent_to_gcp = True


def _create_receipt_received_json(case_id) -> str:
    create_receipt_received = {'case_id': case_id,
                               'response_dateTime': convert_datetime_to_str(datetime.now())}
    return json.dumps(create_receipt_received)
