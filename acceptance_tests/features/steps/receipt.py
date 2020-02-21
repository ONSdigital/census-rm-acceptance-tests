import functools
import json
import time

from behave import when, then, step
from google.api_core.exceptions import GoogleAPIError
from google.cloud import pubsub_v1

from acceptance_tests.utilities.rabbit_helper import start_listening_to_rabbit_queue, store_all_msgs_in_context
from acceptance_tests.utilities.test_case_helper import test_helper
from config import Config


@when("the receipt msg for the created case is put on the GCP pubsub")
def receipt_msg_published_to_gcp_pubsub(context):
    context.first_case = context.case_created_events[0]['payload']['collectionCase']
    for uac in context.uac_created_events:
        if uac['payload']['uac']['caseId'] == context.first_case['id']:
            questionnaire_id = uac['payload']['uac']['questionnaireId']
            break
    else:
        test_helper.fail('Could not find UAC_UPDATED event for receipted case')

    _publish_object_finalize(context, questionnaire_id=questionnaire_id)
    test_helper.assertTrue(context.sent_to_gcp)


@when("the offline receipt msg for the created case is put on the GCP pubsub")
def receipt_offline_msg_published_to_gcp_pubsub(context):
    context.first_case = context.case_created_events[0]['payload']['collectionCase']
    questionnaire_id = context.uac_created_events[0]['payload']['uac']['questionnaireId']
    _publish_offline_receipt(context, questionnaire_id=questionnaire_id)
    test_helper.assertTrue(context.sent_to_gcp)


@when("the offline receipt msg for a continuation form from the case is put on the GCP pubsub")
def continuation_receipt_offline_msg_published_to_gcp_pubsub(context):
    context.first_case = context.case_created_events[0]['payload']['collectionCase']
    questionnaire_id = context.requested_qid
    _publish_offline_receipt(context, questionnaire_id=questionnaire_id)
    test_helper.assertTrue(context.sent_to_gcp)


@then("a uac_updated msg is emitted with active set to false")
def uac_updated_msg_emitted(context):
    context.messages_received = []
    start_listening_to_rabbit_queue(Config.RABBITMQ_RH_OUTBOUND_UAC_QUEUE,
                                    functools.partial(
                                        store_all_msgs_in_context, context=context,
                                        expected_msg_count=1,
                                        type_filter='UAC_UPDATED'))

    test_helper.assertEqual(len(context.messages_received), 1)
    uac = context.messages_received[0]['payload']['uac']
    test_helper.assertEqual(uac['caseId'], context.first_case['id'])
    test_helper.assertFalse(uac['active'])


@step('an ActionCancelled event is sent to field work management with addressType "{address_type}"')
@step('an ActionCancelled Invalid Address event is sent to field work management with addressType "{address_type}"')
def action_cancelled_event_sent_to_fwm(context, address_type):
    context.messages_received = []
    start_listening_to_rabbit_queue(Config.RABBITMQ_OUTBOUND_FIELD_QUEUE, functools.partial(
        _field_work_receipt_callback, context=context))

    test_helper.assertEqual(context.fwmt_emitted_case_id, context.first_case["id"])
    test_helper.assertEqual(context.addressType, address_type)


@step("the offline receipt msg for a continuation form from the case is received")
@step("a receipt for the unlinked UAC-QID pair is received")
def send_receipt_for_unaddressed(context):
    _publish_offline_receipt(context, questionnaire_id=context.expected_questionnaire_id)
    test_helper.assertTrue(context.sent_to_gcp)


@step('a case_updated msg is emitted where "{case_field}" is "{expected_field_value}"')
def case_updated_msg_sent_with_values(context, case_field, expected_field_value):
    context.messages_received = []
    start_listening_to_rabbit_queue(Config.RABBITMQ_RH_OUTBOUND_CASE_QUEUE,
                                    functools.partial(
                                        store_all_msgs_in_context, context=context,
                                        expected_msg_count=1,
                                        type_filter='CASE_UPDATED'))

    test_helper.assertEqual(len(context.messages_received), 1)
    context.first_case = context.messages_received[0]['payload']['collectionCase']
    test_helper.assertEqual(context.first_case['id'], context.first_case['id'])
    test_helper.assertEqual(str(context.first_case[case_field]), expected_field_value)


@step('a case_updated msg is emitted where ceActualResponse is "{actual_responses}" and receipted is "{receipted}"')
def check_ce_actual_responses_and_receipted(context, actual_responses, receipted):
    context.messages_received = []
    start_listening_to_rabbit_queue(Config.RABBITMQ_RH_OUTBOUND_CASE_QUEUE,
                                    functools.partial(
                                        store_all_msgs_in_context, context=context,
                                        expected_msg_count=1,
                                        type_filter='CASE_UPDATED'))

    test_helper.assertEqual(len(context.messages_received), 1)
    context.first_case = context.messages_received[0]['payload']['collectionCase']
    test_helper.assertEqual(context.first_case['id'], context.first_case['id'])

    test_helper.assertEqual(str(context.first_case['ceActualResponses']), actual_responses)
    test_helper.assertEqual(str(context.first_case['receiptReceived']), receipted)


def _field_work_receipt_callback(ch, method, _properties, body, context):
    action_close = json.loads(body)

    if not action_close['actionInstruction'] == 'CLOSE':
        ch.basic_nack(delivery_tag=method.delivery_tag)
        test_helper.fail('Unexpected message on Action.Field case queue, wanted CLOSE')

    context.addressType = action_close['addressType']
    context.fwmt_emitted_case_id = action_close['caseId']
    ch.basic_ack(delivery_tag=method.delivery_tag)
    ch.stop_consuming()


def _publish_object_finalize(context, case_id="0", tx_id="3d14675d-a25d-4672-a0fe-b960586653e8", questionnaire_id="0"):
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


def _publish_offline_receipt(context, tx_id="3d14675d-a25d-4672-a0fe-b960586653e8", questionnaire_id="0"):
    context.sent_to_gcp = False

    publisher = pubsub_v1.PublisherClient()

    topic_path = publisher.topic_path(Config.OFFLINE_RECEIPT_TOPIC_PROJECT, Config.OFFLINE_RECEIPT_TOPIC_ID)

    data = json.dumps({
        "dateTime": "2008-08-24T00:00:00",
        "transactionId": tx_id,
        "questionnaireId": questionnaire_id,
        "channel": "PQRS"
    })

    future = publisher.publish(topic_path,
                               data=data.encode('utf-8'))

    if not future.done():
        time.sleep(1)
    try:
        future.result(timeout=30)
    except GoogleAPIError:
        return

    print(f'Message published to {topic_path}')

    context.sent_to_gcp = True


@when("the receipt msg is put on the GCP pubsub for the telephone capture qid")
def send_receipt_with_telephone_individual_qid(context):
    individual_qid = context.telephone_capture_qid_uac['questionnaireId']

    _publish_object_finalize(context, questionnaire_id=individual_qid)
    test_helper.assertTrue(context.sent_to_gcp)
