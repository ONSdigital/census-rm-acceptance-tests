import functools
import json

import requests
from behave import then, when, step

from acceptance_tests.utilities.rabbit_helper import start_listening_to_rabbit_queue, store_all_msgs_in_context
from config import Config

caseapi_uacqid_pair_url = f'{Config.CASEAPI_SERVICE}/uacqid/create'


@when('a UAC/QID pair is requested with questionnaire type "{questionnaire_type}"')
def generate_post_request_body(context, questionnaire_type):
    context.first_case = context.case_created_events[0]['payload']['collectionCase']
    context.uacqid_json = {"questionnaireType": questionnaire_type,
                           "caseId": context.first_case['id']}
    headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
    context.response = requests.post(url=caseapi_uacqid_pair_url, data=json.dumps(context.uacqid_json), headers=headers)


@then('case API should return a  new UAC and QID with correct questionnaire type')
def generate_uacqid_pair(context):
    assert context.response.status_code == 201
    response_data = json.loads(context.response.content)
    assert 'uac' in response_data, 'uac missing in response'
    assert 'qid' in response_data, 'qid missing in response'
    assert context.uacqid_json["questionnaireType"] == response_data['qid'][:2]


@step('a UAC updated message with "{questionnaire_type}" questionnaire type is emitted')
def listen_for_ad_hoc_uac_updated_message(context, questionnaire_type):
    context.messages_received = []
    start_listening_to_rabbit_queue(Config.RABBITMQ_RH_OUTBOUND_UAC_QUEUE_TEST,
                                    functools.partial(store_all_msgs_in_context, context=context,
                                                      expected_msg_count=1,
                                                      type_filter='UAC_UPDATED'))
    uac_updated_event = context.messages_received[0]
    assert uac_updated_event['payload']['uac']['caseId'] == context.first_case['id'], \
        'Fulfilment request UAC updated event found with wrong case ID'
    assert uac_updated_event['payload']['uac']['questionnaireId'].startswith(questionnaire_type), \
        'Fulfilment request UAC updated event found with wrong questionnaire type'
    context.requested_uac = uac_updated_event['payload']['uac']['uac']
    context.requested_qid = uac_updated_event['payload']['uac']['questionnaireId']

    context.case_for_events_check = {'id': uac_updated_event['payload']['uac']['caseId']}
