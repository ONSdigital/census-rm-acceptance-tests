import functools
import json
import time

from behave import when, then, step
from google.api_core.exceptions import GoogleAPIError
from google.cloud import pubsub_v1

from acceptance_tests.utilities.rabbit_helper import start_listening_to_rabbit_queue, store_all_msgs_in_context
from config import Config


@step("the correct case and uac are emitted")
def correct_case_and_uac_emitted(context):
    context.messages_received = []
    start_listening_to_rabbit_queue(Config.RABBITMQ_RH_OUTBOUND_UAC_QUEUE_TEST,
                                    functools.partial(store_all_msgs_in_context, context=context,
                                                      expected_msg_count=1, type_filter='UAC_UPDATED'))

    assert len(context.messages_received) == 1

    context.messages_received = []
    start_listening_to_rabbit_queue(Config.RABBITMQ_RH_OUTBOUND_CASE_QUEUE_TEST,
                                    functools.partial(store_all_msgs_in_context, context=context,
                                                      expected_msg_count=1, type_filter='CASE_CREATED'))
    assert len(context.messages_received) == 1
    context.emitted_case = context.messages_received[0]['payload']['collectionCase']
    assert context.emitted_case['address']['arid'] == context.sample_units[0]['attributes']['ARID']


@when("the receipt msg for the created case is put on the GCP pubsub")
def receipt_msg_published_to_gcp_pubsub(context):
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
