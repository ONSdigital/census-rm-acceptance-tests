import functools
import json

from behave import step

from acceptance_tests.features.steps.case_look_up import get_ccs_qid_for_case_id
from acceptance_tests.features.steps.event_log import check_if_event_list_is_exact_match
from acceptance_tests.features.steps.fulfilment import send_print_fulfilment_request
from acceptance_tests.features.steps.telephone_capture import request_individual_telephone_capture, \
    check_correct_uac_updated_message_is_emitted, request_hi_individual_telephone_capture
from acceptance_tests.features.steps.unaddressed import send_questionnaire_linked_msg_to_rabbit, \
    check_uac_message_is_received
from acceptance_tests.utilities.pubsub_helper import publish_to_pubsub
from acceptance_tests.utilities.rabbit_context import RabbitContext
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
    _publish_offline_receipt(context, channel='PQRS', unreceipt=False, questionnaire_id=questionnaire_id)
    test_helper.assertTrue(context.sent_to_gcp)


@step("the offline receipt msg for the receipted case is put on the GCP pubsub")
def offline_msg_published_to_gcp_pubsub_for_receipted_cases(context):
    context.first_case = context.receipting_case
    questionnaire_id = context.qid_to_receipt
    _publish_offline_receipt(context, channel='PQRS', unreceipt=False, questionnaire_id=questionnaire_id)
    test_helper.assertTrue(context.sent_to_gcp)


@step("the offline receipt msg for the unlinked is put on the GCP pubsub")
def offline_msg_published_to_gcp_pubsub_for_unlinked_qids(context):
    questionnaire_id = context.expected_questionnaire_id
    _publish_offline_receipt(context, channel='PQRS', unreceipt=False, questionnaire_id=questionnaire_id)
    test_helper.assertTrue(context.sent_to_gcp)


@step("a blank questionnaire receipts comes in for an unlinked qid")
def offline_receipt_for_an_unlinked_qid(context):
    context.first_case = context.receipting_case
    questionnaire_id = context.expected_questionnaire_id
    _publish_offline_receipt(context, channel="QM", questionnaire_id=questionnaire_id, unreceipt=True)
    test_helper.assertTrue(context.sent_to_gcp)


@step("the offline receipt msg for a continuation form from the case is put on the GCP pubsub")
def continuation_receipt_offline_msg_published_to_gcp_pubsub(context):
    context.first_case = context.case_created_events[0]['payload']['collectionCase']
    questionnaire_id = context.requested_qid
    _publish_offline_receipt(context, questionnaire_id=questionnaire_id)
    test_helper.assertTrue(context.sent_to_gcp)


@step("the blank questionnaire msg for a case is put on the GCP pubsub")
def blank_questionnaire_msg_published_to_gcp_pubsubs(context):
    context.first_case = context.receipting_case
    questionnaire_id = context.qid_to_receipt
    _publish_offline_receipt(context, channel="QM", questionnaire_id=questionnaire_id, unreceipt=True)
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


@step("a uac_updated msg is emitted with active set to false")
def uac_updated_msg_emitted(context):
    emitted_uac = _get_emitted_uac(context)
    test_helper.assertEqual(emitted_uac['caseId'], context.first_case['id'])
    test_helper.assertFalse(emitted_uac['active'])


@step('a CANCEL action instruction is sent to field work management with address type "{address_type}"')
def action_cancel_sent_to_fwm(context, address_type):
    context.messages_received = []
    start_listening_to_rabbit_queue(Config.RABBITMQ_OUTBOUND_FIELD_QUEUE, functools.partial(
        _field_work_cancel_callback, context=context))

    test_helper.assertEqual(context.fwmt_emitted_case_id, context.first_case["id"])
    test_helper.assertEqual(context.addressType, address_type)
    test_helper.assertEqual(context.field_action_cancel_message['surveyName'], context.first_case['survey'])


@step("the offline receipt msg for a continuation form from the case is received")
@step("a receipt for the unlinked UAC-QID pair is received")
def send_receipt_for_unaddressed(context):
    _publish_offline_receipt(context, questionnaire_id=context.expected_questionnaire_id)
    test_helper.assertTrue(context.sent_to_gcp)


@step('a case_updated msg is emitted where "{case_field}" is "{expected_field_value}"')
@step(
    'a case_updated msg of type "{case_type}" and address level "{address_level}" is emitted where "{case_field}" is '
    '"{expected_field_value}" and qid is "{another_qid_needed}"')
def case_updated_msg_sent_with_values(context, case_field, expected_field_value, address_level=None, case_type=None,
                                      another_qid_needed=None):
    if another_qid_needed == 'True' or address_level == 'E':
        return
    emitted_case = _get_emitted_case(context)

    if case_type != "HI":
        test_helper.assertEqual(emitted_case['id'], context.first_case['id'])
        test_helper.assertEqual(str(emitted_case[case_field]), expected_field_value)
    else:
        test_helper.assertEqual(emitted_case['id'], context.receipting_case['id'])
        test_helper.assertEqual(str(emitted_case[case_field]), expected_field_value)


def _field_work_cancel_callback(ch, method, _properties, body, context):
    action_cancel = json.loads(body)

    if not action_cancel['actionInstruction'] == 'CANCEL':
        ch.basic_nack(delivery_tag=method.delivery_tag)
        test_helper.fail(f'Unexpected message on {Config.RABBITMQ_OUTBOUND_FIELD_QUEUE} case queue. '
                         f'Got "{action_cancel["actionInstruction"]}", wanted "CANCEL"')

    context.addressType = action_cancel['addressType']
    context.fwmt_emitted_case_id = action_cancel['caseId']
    context.field_action_cancel_message = action_cancel
    ch.basic_ack(delivery_tag=method.delivery_tag)
    ch.stop_consuming()


def _publish_object_finalize(context, case_id="0", tx_id="3d14675d-a25d-4672-a0fe-b960586653e8", questionnaire_id="0"):
    context.sent_to_gcp = False

    data = json.dumps({
        "timeCreated": "2008-08-24T00:00:00Z",
        "metadata": {
            "case_id": case_id,
            "tx_id": tx_id,
            "questionnaire_id": questionnaire_id,
        }
    })

    publish_to_pubsub(data,
                      Config.RECEIPT_TOPIC_PROJECT,
                      Config.RECEIPT_TOPIC_ID,
                      eventType='OBJECT_FINALIZE',
                      bucketId='eq-bucket',
                      objectId=tx_id)

    context.sent_to_gcp = True


def _publish_offline_receipt(context, channel='QM', unreceipt=False,
                             tx_id="3d14675d-a25d-4672-a0fe-b960586653e8", questionnaire_id="0"):
    context.sent_to_gcp = False

    data = json.dumps({
        "dateTime": "2008-08-24T00:00:00",
        "transactionId": tx_id,
        "questionnaireId": questionnaire_id,
        "channel": channel,
        "unreceipt": unreceipt
    })
    publish_to_pubsub(data, Config.OFFLINE_RECEIPT_TOPIC_PROJECT, Config.OFFLINE_RECEIPT_TOPIC_ID)

    context.sent_to_gcp = True


@step('we have retrieved the case and QID to receipt')
def get_first_case_and_linked_qid_to_receipt(context):
    context.loaded_case = context.case_created_events[0]['payload']['collectionCase']
    context.receipting_case = context.case_created_events[0]['payload']['collectionCase']
    context.qid_to_receipt = context.uac_created_events[0]['payload']['uac']['questionnaireId']


@step('if required, a new qid and case are created for case type "{case_type}" address level "{address_level}"'
      ' qid type "{qid_type}" and country "{country_code}"')
@step('a new qid and case are created for case type "{case_type}" address level "{address_level}"'
      ' qid type "{qid_type}" and country "{country_code}"')
def get_new_qid_and_case_as_required(context, case_type, address_level, qid_type, country_code):
    context.loaded_case = context.case_created_events[0]['payload']['collectionCase']
    # receipting_case will be over written if a child case is created
    context.receipting_case = context.case_created_events[0]['payload']['collectionCase']

    if qid_type in ['HH', 'CE1']:
        context.qid_to_receipt = context.uac_created_events[0]['payload']['uac']['questionnaireId']
        return

    if qid_type == 'Ind':
        if case_type == 'HI':
            context.case_type = "HI"
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


@step('if required for "{questionnaire_type}", a new qid is created "{qid_needed}"')
def get_second_qid(context, questionnaire_type, qid_needed):
    if qid_needed == 'True':
        context.first_case = context.case_created_events[0]['payload']['collectionCase']

        with RabbitContext(queue_name=Config.RABBITMQ_UNADDRESSED_REQUEST_QUEUE) as rabbit:
            rabbit.publish_message(
                message=json.dumps({'questionnaireType': questionnaire_type}),
                content_type='application/json')

        listen_for_ad_hoc_uac_updated_message(context, questionnaire_type)
        send_questionnaire_linked_msg_to_rabbit(context.requested_qid, context.first_case['id'])
        _get_emitted_uac(context)  # Throw away the linked message - we don't need it and it breaks subsequent steps
        context.qid_to_receipt = context.requested_qid


@step("the receipt msg is put on the GCP pubsub")
@step("the eQ receipt msg is put on the GCP pubsub")
def send_receipt(context):
    _publish_object_finalize(context, questionnaire_id=context.qid_to_receipt)
    test_helper.assertTrue(context.sent_to_gcp)


@step('if the actual response count is incremented "{incremented}" or the case is marked receipted "{receipted}" '
      'then there should be a case updated message of case type "{case_type}"')
def check_ce_actual_responses_and_receipted(context, incremented, receipted, case_type):
    if receipted == 'False' and incremented == 'False':
        # The case has not changed, so there's nothing to see here
        check_no_msgs_sent_to_queue(context, Config.RABBITMQ_RH_OUTBOUND_CASE_QUEUE, functools.partial(
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

    test_helper.assertEqual(str(emitted_case['receiptReceived']), str(receipted),
                            "Receipted status on case updated event does not match expected")


@step('if the field instruction "{action_instruction_type}" is not NONE a msg to field is emitted')
@step('the field instruction is "{action_instruction_type}"')
@step('an "{action_instruction_type}" field instruction is emitted')
@step('a "{action_instruction_type}" field instruction is emitted')
def check_receipt_to_field_msg(context, action_instruction_type):
    if action_instruction_type == 'NONE':
        check_no_msgs_sent_to_queue(context, Config.RABBITMQ_OUTBOUND_FIELD_QUEUE, functools.partial(
            store_all_msgs_in_context, context=context,
            expected_msg_count=0), timeout=1)
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


@step('a case_updated msg has not been emitted')
def check_receipt_to_field_msg_is_none(context):
    context.messages_received = []
    check_no_msgs_sent_to_queue(context, Config.RABBITMQ_RH_OUTBOUND_CASE_QUEUE, functools.partial(
        store_all_msgs_in_context, context=context,
        expected_msg_count=0), timeout=3)

    assert len(context.messages_received) == 0


@step('the correct events are logged for loaded case events "{loaded_case_events}" '
      'and individual case events "{individual_case_events}"')
@step('the correct events are logged for loaded case events "{loaded_case_events}" for blank questionnaire')
def check_events_logged_on_loaded_and_ind_case(context, loaded_case_events, individual_case_events=None):
    check_if_event_list_is_exact_match(loaded_case_events, context.loaded_case['id'])

    if individual_case_events and len(individual_case_events.replace('[', '').replace(']', '')) > 0:
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


@step('a UAC updated message with "{questionnaire_type}" questionnaire type is emitted')
def listen_for_ad_hoc_uac_updated_message(context, questionnaire_type):
    context.messages_received = []
    start_listening_to_rabbit_queue(Config.RABBITMQ_RH_OUTBOUND_UAC_QUEUE,
                                    functools.partial(store_all_uac_updated_msgs,
                                                      context=context))
    uac_updated_event = context.messages_received[0]
    context.requested_uac = uac_updated_event['payload']['uac']['uac']
    context.requested_qid = uac_updated_event['payload']['uac']['questionnaireId']


def store_all_uac_updated_msgs(ch, method, _properties, body, context):
    parsed_body = json.loads(body)
    context.messages_received.append(parsed_body)
    ch.basic_ack(delivery_tag=method.delivery_tag)
    ch.stop_consuming()


@step(
    "the offline receipt msg for the receipted case is put on the GCP pubsub and expected uac inactive msg is emitted")
def offline_msg_published_to_gcp_pubsub_for_receipted_cases_and_wait_for_inactive_uac_msg(context):
    offline_msg_published_to_gcp_pubsub_for_receipted_cases(context)
    check_uac_updated_msg_sets_receipted_qid_to_unactive(context)


@step("the blank questionnaire msg for a case is put on the GCP pubsub and expected uac inactive msg is emitted")
def blank_questionnaire_published_to_gcp_pubsub_and_wait_for_inactive_uac_msg(context):
    blank_questionnaire_msg_published_to_gcp_pubsubs(context)
    check_uac_updated_msg_sets_receipted_qid_to_unactive(context)


@step("the offline receipt msg for the unlinked is put on the GCP pubsub and the unlinked uac is emitted as inactive")
def offline_msg_published_to_gcp_pubsub_for_unlinked_qids_and_uac_emitted(context):
    offline_msg_published_to_gcp_pubsub_for_unlinked_qids(context)
    check_uac_message_is_received(context)


@step("a blank questionnaire receipts comes in for an unlinked qid and the correct uac msg is emitted")
def offline_receipt_for_an_unlinked_qid_and_uac_emitted(context):
    offline_receipt_for_an_unlinked_qid(context)
    check_uac_message_is_received(context)


@step("the receipt msg is put on the GCP pubsub and a uac_updated msg is emitted")
def send_receipt_and_check_inactive_uac_emitted(context):
    send_receipt(context)
    check_uac_updated_msg_sets_receipted_qid_to_unactive(context)
