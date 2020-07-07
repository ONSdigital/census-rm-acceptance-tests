import functools
import uuid

import requests

from acceptance_tests.utilities.rabbit_helper import start_listening_to_rabbit_queue, \
    store_all_uac_updated_msgs_by_collection_exercise_id
from acceptance_tests.utilities.test_case_helper import test_helper
from config import Config


def request_individual_telephone_capture(context, address_type, country_code):
    context.first_case = context.case_created_events[0]['payload']['collectionCase']
    context.fulfilment_requested_case_id = context.case_created_events[0]['payload']['collectionCase']['id']
    check_address_type_country(context.first_case, address_type, country_code)

    response = requests.get(
        f"{Config.CASE_API_CASE_URL}/{context.first_case['id']}/qid?individual=true")
    response.raise_for_status()

    context.telephone_capture_qid_uac = response.json()


def check_correct_uac_updated_message_is_emitted(context):
    context.messages_received = []
    start_listening_to_rabbit_queue(Config.RABBITMQ_RH_OUTBOUND_UAC_QUEUE,
                                    functools.partial(store_all_uac_updated_msgs_by_collection_exercise_id,
                                                      context=context,
                                                      expected_msg_count=1,
                                                      collection_exercise_id=context.collection_exercise_id))

    uac_updated_payload = context.messages_received[0]['payload']['uac']
    test_helper.assertEqual(uac_updated_payload['caseId'], context.first_case['id'],
                            'UAC updated event case ID does not match the case it was requested for')
    test_helper.assertEqual(uac_updated_payload['uac'], context.telephone_capture_qid_uac['uac'],
                            'UAC updated event UAC does not match what the API returned')
    test_helper.assertEqual(uac_updated_payload['questionnaireId'],
                            context.telephone_capture_qid_uac['questionnaireId'],
                            'UAC updated event QID does not match what the API returned')


def check_address_type_country(case, address_type, country_code):
    test_helper.assertEqual(country_code, case['address']['region'][0],
                            'Loaded case does not match expected region')
    test_helper.assertEqual(address_type, case['address']['addressType'],
                            'Loaded case does not match expected address type')


def request_hi_individual_telephone_capture(context, address_type, country_code):
    context.first_case = context.case_created_events[0]['payload']['collectionCase']
    context.telephone_capture_parent_case_id = context.first_case['id']
    context.individual_case_id = str(uuid.uuid4())
    check_address_type_country_address_level(context.first_case, address_type, country_code)
    response = requests.get(
        f"{Config.CASEAPI_SERVICE}/cases/{context.first_case['id']}/qid"
        f"?individual=true"
        f"&individualCaseId={context.individual_case_id}")
    response.raise_for_status()

    context.telephone_capture_qid_uac = response.json()


def check_address_type_country_address_level(case, address_type, country_code, address_level='U'):
    check_address_type_country(case, address_type, country_code)
    test_helper.assertEqual(address_level, case['address']['addressLevel'],
                            'Loaded case does does not have unit address level')
