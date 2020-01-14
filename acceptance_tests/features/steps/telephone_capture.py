import functools

import requests
from behave import step

from acceptance_tests.utilities.rabbit_helper import start_listening_to_rabbit_queue, store_all_msgs_in_context
from acceptance_tests.utilities.test_case_helper import test_helper
from config import Config


@step('there is a request for telephone capture for an english respondent with case type HH')
def request_telephone_capture_qid_uac(context):
    context.first_case = context.case_created_events[0]['payload']['collectionCase']
    response = requests.get(f"{Config.CASEAPI_SERVICE}/cases/{context.first_case['id']}/qid")
    test_helper.assertEqual(response.status_code, 200)

    context.telephone_capture_qid_uac = response.json()


@step('a UAC and QID with questionnaire type "{questionnaire_type}" type are generated and returned')
def check_telephone_capture_uac_and_qid_type(context, questionnaire_type):
    test_helper.assertIsNotNone(context.telephone_capture_qid_uac.get('uac'))
    test_helper.assertEqual(context.telephone_capture_qid_uac['questionnaireId'][:2], questionnaire_type)


@step('a UAC updated event is emitted linking the new UAC and QID to the requested case')
def check_correct_uac_updated_message_is_emitted(context):
    context.messages_received = []
    start_listening_to_rabbit_queue(Config.RABBITMQ_RH_OUTBOUND_UAC_QUEUE_TEST,
                                    functools.partial(store_all_msgs_in_context, context=context,
                                                      expected_msg_count=1,
                                                      type_filter='UAC_UPDATED'))

    uac_updated_payload = context.messages_received[0]['payload']['uac']
    test_helper.assertEqual(uac_updated_payload['caseId'], context.first_case['id'],
                            'UAC updated event case ID does not match the case it was requested for')
    test_helper.assertEqual(uac_updated_payload['uac'], context.telephone_capture_qid_uac['uac'],
                            'UAC updated event UAC does not match what the API returned')
    test_helper.assertEqual(uac_updated_payload['questionnaireId'],
                            context.telephone_capture_qid_uac['questionnaireId'],
                            'UAC updated event QID does not match what the API returned')
