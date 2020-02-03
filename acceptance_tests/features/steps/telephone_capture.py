import functools
import uuid

import requests
from behave import step

from acceptance_tests.utilities.event_helper import check_individual_child_case_is_emitted
from acceptance_tests.utilities.rabbit_helper import start_listening_to_rabbit_queue, store_all_msgs_in_context
from acceptance_tests.utilities.test_case_helper import test_helper
from config import Config


@step('there is a request for telephone capture for an address level "{address_level}" case '
      'with case type "{case_type}" and country "{country_code}"')
def request_telephone_capture_qid_uac(context, address_level, case_type, country_code):
    context.first_case = context.case_created_events[0]['payload']['collectionCase']
    context.fulfilment_requested_case_id = context.case_created_events[0]['payload']['collectionCase']['id']
    _check_case_type_country_address_level(context.first_case, case_type, country_code, address_level=address_level)
    response = requests.get(f"{Config.CASEAPI_SERVICE}/cases/{context.first_case['id']}/qid")
    test_helper.assertEqual(response.status_code, 200)

    context.telephone_capture_qid_uac = response.json()


@step('there is a request for individual telephone capture for a unit case '
      'with case type "{case_type}" and country "{country_code}"')
def request_individual_telephone_capture_qid_uac(context, case_type, country_code):
    context.first_case = context.case_created_events[0]['payload']['collectionCase']
    context.telephone_capture_parent_case_id = context.first_case['id']
    context.individual_case_id = str(uuid.uuid4())
    _check_case_type_country_address_level(context.first_case, case_type, country_code)
    response = requests.get(
        f"{Config.CASEAPI_SERVICE}/cases/{context.first_case['id']}/qid"
        f"?individual=true"
        f"&individualCaseId={context.individual_case_id}")
    response.raise_for_status()

    context.telephone_capture_qid_uac = response.json()


def _check_case_type_country_address_level(case, case_type, country_code, address_level='U'):
    test_helper.assertEqual(country_code, case['treatmentCode'][-1],
                            'Loaded case does not match expected nationality')
    test_helper.assertEqual(case_type, case['treatmentCode'].split('_')[0],
                            'Loaded case does not match expected case type')
    test_helper.assertEqual(address_level, case['address']['addressLevel'],
                            'Loaded case does does not have unit address level')


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


@step('a UAC updated event is emitted linking the new UAC and QID to the individual case')
def check_correct_individual_uac_updated_message_is_emitted(context):
    context.messages_received = []
    start_listening_to_rabbit_queue(Config.RABBITMQ_RH_OUTBOUND_UAC_QUEUE_TEST,
                                    functools.partial(store_all_msgs_in_context, context=context,
                                                      expected_msg_count=1,
                                                      type_filter='UAC_UPDATED'))

    uac_updated_payload = context.messages_received[0]['payload']['uac']
    test_helper.assertEqual(uac_updated_payload['caseId'], context.individual_case_id,
                            'UAC updated event case ID does not match the case it was requested for')
    test_helper.assertEqual(uac_updated_payload['uac'], context.telephone_capture_qid_uac['uac'],
                            'UAC updated event UAC does not match what the API returned')
    test_helper.assertEqual(uac_updated_payload['questionnaireId'],
                            context.telephone_capture_qid_uac['questionnaireId'],
                            'UAC updated event QID does not match what the API returned')


@step('a new individual child case for telephone capture is emitted to RH and Action Scheduler')
def telephone_capture_child_case_is_emitted(context):
    check_individual_child_case_is_emitted(context, context.telephone_capture_parent_case_id,
                                           context.individual_case_id)


@step("there is a request for individual telephone capture for and estab case")
def spg_unit_individual_request(context):
    context.first_case = context.case_created_events[0]['payload']['collectionCase']
    context.fulfilment_requested_case_id = context.case_created_events[0]['payload']['collectionCase']['id']

    response = requests.get(
        f"{Config.CASEAPI_SERVICE}/cases/{context.first_case['id']}/qid?individual=true")
    response.raise_for_status()

    context.telephone_capture_qid_uac = response.json()
