import functools
import json
import time

from behave import when, then, step
from google.api_core.exceptions import GoogleAPIError
from google.cloud import pubsub_v1

from acceptance_tests.features.steps.ad_hoc_uac_qid import listen_for_ad_hoc_uac_updated_message
from acceptance_tests.features.steps.case_look_up import get_ccs_qid_for_case_id
from acceptance_tests.features.steps.event_log import check_if_event_list_is_exact_match
from acceptance_tests.features.steps.fulfilment_request import send_print_fulfilment_request
from acceptance_tests.features.steps.telephone_capture import request_individual_telephone_capture, \
    check_correct_uac_updated_message_is_emitted, request_hi_individual_telephone_capture
from acceptance_tests.utilities.rabbit_helper import start_listening_to_rabbit_queue, store_all_msgs_in_context, \
    check_no_msgs_sent_to_queue
from acceptance_tests.utilities.test_case_helper import test_helper
from config import Config


@step("the receipt msg for the created case is put on the GCP pubsub")
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


@step("the offline receipt msg for the created case is put on the GCP pubsub")
def receipt_offline_msg_published_to_gcp_pubsub(context):
    context.first_case = context.case_created_events[0]['payload']['collectionCase']
    questionnaire_id = context.uac_created_events[0]['payload']['uac']['questionnaireId']
    _publish_offline_receipt(context, questionnaire_id=questionnaire_id)
    test_helper.assertTrue(context.sent_to_gcp)


@step("the offline receipt msg for a continuation form from the case is put on the GCP pubsub")
def continuation_receipt_offline_msg_published_to_gcp_pubsub(context):
    context.first_case = context.case_created_events[0]['payload']['collectionCase']
    questionnaire_id = context.requested_qid
    _publish_offline_receipt(context, questionnaire_id=questionnaire_id)
    test_helper.assertTrue(context.sent_to_gcp)


@step("the receipt msg for the created CCS case is put on the GCP pubsub")
def receipt_ccs_offline_msg_published_to_gcp_pubsub(context):
    context.first_case = context.ccs_case

    # TODO: Other tests match on this key structure. Remove when we've settled on case API fields
    context.first_case['survey'] = context.ccs_case['surveyType']

    response = get_ccs_qid_for_case_id(context.ccs_case['id'])
    questionnaire_id = response['questionnaireId']
    _publish_object_finalize(context, questionnaire_id=questionnaire_id)
    test_helper.assertTrue(context.sent_to_gcp)


@then("a uac_updated msg is emitted with active set to false")
def uac_updated_msg_emitted(context):
    emitted_uac = _get_emitted_uac(context)
    test_helper.assertEqual(emitted_uac['caseId'], context.first_case['id'])
    test_helper.assertFalse(emitted_uac['active'])


@step('a CLOSE action instruction is sent to field work management with addressType "{address_type}"')
def action_close_sent_to_fwm(context, address_type):
    context.messages_received = []
    start_listening_to_rabbit_queue(Config.RABBITMQ_OUTBOUND_FIELD_QUEUE, functools.partial(
        _field_work_close_callback, context=context))

    test_helper.assertEqual(context.fwmt_emitted_case_id, context.first_case["id"])
    test_helper.assertEqual(context.addressType, address_type)
    test_helper.assertEqual(context.field_action_close_message['surveyName'], context.first_case['survey'])


@step("the offline receipt msg for a continuation form from the case is received")
@step("a receipt for the unlinked UAC-QID pair is received")
def send_receipt_for_unaddressed(context):
    _publish_offline_receipt(context, questionnaire_id=context.expected_questionnaire_id)
    test_helper.assertTrue(context.sent_to_gcp)


@step('a case_updated msg is emitted where "{case_field}" is "{expected_field_value}"')
def case_updated_msg_sent_with_values(context, case_field, expected_field_value):
    emitted_case = _get_emitted_case(context)

    test_helper.assertEqual(emitted_case['id'], context.first_case['id'])
    test_helper.assertEqual(str(emitted_case[case_field]), expected_field_value)


def _field_work_close_callback(ch, method, _properties, body, context):
    action_close = json.loads(body)

    if not action_close['actionInstruction'] == 'CLOSE':
        ch.basic_nack(delivery_tag=method.delivery_tag)
        test_helper.fail(f'Unexpected message on {Config.RABBITMQ_OUTBOUND_FIELD_QUEUE} case queue. '
                         f'Got "{action_close["actionInstruction"]}", wanted "CLOSE"')

    context.addressType = action_close['addressType']
    context.fwmt_emitted_case_id = action_close['caseId']
    context.field_action_close_message = action_close
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


@step('if required a new qid and case are created for "{case_type}" "{address_level}" "{qid_type}" "{country_code}"')
def get_new_qid_and_case_as_required(context, case_type, address_level, qid_type, country_code):
    context.loaded_case = context.case_created_events[0]['payload']['collectionCase']
    # receipting_case will be over written if a child case is created
    context.receipting_case = context.case_created_events[0]['payload']['collectionCase']

    if qid_type in ['HH', 'CE1']:
        context.qid_to_receipt = context.uac_created_events[0]['payload']['uac']['questionnaireId']
        return

    if qid_type == 'Ind':
        if case_type == 'HI':
            request_hi_individual_telephone_capture(context, "HH", country_code)
            context.qid_to_receipt = context.telephone_capture_qid_uac['questionnaireId']
            context.receipting_case = _get_emitted_case(context, 'CASE_CREATED')

            uac = _get_emitted_uac(context)
            test_helper.assertEqual(uac['caseId'], context.receipting_case['id'])
            test_helper.assertEquals(uac['questionnaireId'], context.qid_to_receipt)

            return
        else:
            request_individual_telephone_capture(context, case_type, country_code)
            context.qid_to_receipt = context.telephone_capture_qid_uac['questionnaireId']
            check_correct_uac_updated_message_is_emitted(context)
            return

    if qid_type == 'Cont':
        send_print_fulfilment_request(context, "P_OR_HC1")
        listen_for_ad_hoc_uac_updated_message(context, "11")
        context.qid_to_receipt = context.requested_qid
        return

    test_helper.assertFalse(f"Failed to get qid for {qid_type}")


@when("the receipt msg is put on the GCP pubsub")
def send_receipt(context):
    _publish_object_finalize(context, questionnaire_id=context.qid_to_receipt)
    test_helper.assertTrue(context.sent_to_gcp)


@step('if the case is updated by an "{incremented}" or by a "{receipted}" '
      'then there should be a case updated message of "{case_type}"')
def check_ce_actual_responses_and_receipted(context, incremented, receipted, case_type):
    if receipted == 'False' and incremented == 'False':
        # The case has not changed, so there's nothing to see here
        check_no_msgs_sent_to_queue(Config.RABBITMQ_RH_OUTBOUND_CASE_QUEUE,
                                    functools.partial(
                                        store_all_msgs_in_context, context=context,
                                        expected_msg_count=0), timeout=3)
        return

    emitted_case = _get_emitted_case(context)
    test_helper.assertEqual(emitted_case['id'], context.receipting_case['id'])

    # ceActualResponses is not set on HI cases
    if case_type != "HI":
        expected_actual_responses = context.receipting_case['ceActualResponses']

        if incremented == 'True':
            expected_actual_responses = expected_actual_responses + 1

        test_helper.assertEqual(emitted_case['ceActualResponses'], expected_actual_responses)

    if receipted == 'AR >= E':
        receipted = emitted_case['ceActualResponses'] >= emitted_case['ceExpectedCapacity']

    test_helper.assertEqual(str(emitted_case['receiptReceived']), str(receipted))


@step('if the "{action_instruction_type}" is not NONE a msg to field is emitted '
      'where ceActualResponse is "{incremented}" with action instruction')
def check_receipt_to_field_msg(context, action_instruction_type, incremented):
    if action_instruction_type == 'NONE':
        check_no_msgs_sent_to_queue(Config.RABBITMQ_OUTBOUND_FIELD_QUEUE,
                                    functools.partial(
                                        store_all_msgs_in_context, context=context,
                                        expected_msg_count=0), timeout=3)
        return

    context.messages_received = []
    start_listening_to_rabbit_queue(Config.RABBITMQ_OUTBOUND_FIELD_QUEUE,
                                    functools.partial(
                                        store_all_msgs_in_context, context=context,
                                        expected_msg_count=1))

    msg_to_field = context.messages_received[0]
    test_helper.assertEquals(msg_to_field['caseId'], context.receipting_case['id'])
    test_helper.assertEquals(msg_to_field['actionInstruction'], action_instruction_type)
    test_helper.assertEqual(msg_to_field['surveyName'], context.receipting_case['survey'])


@step('the correct events are logged for "{loaded_case_events}" and "{individual_case_events}"')
def check_events_logged_on_loaded_and_ind_case(context, loaded_case_events, individual_case_events):
    check_if_event_list_is_exact_match(loaded_case_events, context.loaded_case['id'])

    if len(individual_case_events.replace('[', '').replace(']', '')) > 0:
        check_if_event_list_is_exact_match(individual_case_events, context.receipting_case['id'])


@step("a uac_updated msg is emitted with active set to false for the receipted qid")
def check_uac_updated_msg_sets_receipted_qid_to_unactive(context):
    uac = _get_emitted_uac(context)
    test_helper.assertEqual(uac['caseId'], context.receipting_case['id'])
    test_helper.assertEquals(uac['questionnaireId'], context.qid_to_receipt)
    test_helper.assertFalse(uac['active'])


def _get_emitted_case(context, type_filter='CASE_UPDATED'):
    context.messages_received = []
    start_listening_to_rabbit_queue(Config.RABBITMQ_RH_OUTBOUND_CASE_QUEUE,
                                    functools.partial(
                                        store_all_msgs_in_context, context=context,
                                        expected_msg_count=1,
                                        type_filter=type_filter))

    test_helper.assertEqual(len(context.messages_received), 1)

    return context.messages_received[0]['payload']['collectionCase']


def _get_emitted_uac(context):
    context.messages_received = []
    start_listening_to_rabbit_queue(Config.RABBITMQ_RH_OUTBOUND_UAC_QUEUE,
                                    functools.partial(
                                        store_all_msgs_in_context, context=context,
                                        expected_msg_count=1,
                                        type_filter='UAC_UPDATED'))

    test_helper.assertEqual(len(context.messages_received), 1)

    return context.messages_received[0]['payload']['uac']
