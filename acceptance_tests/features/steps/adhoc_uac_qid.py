import requests
import json

from behave import then, when
from config import Config

caseapi_uacqid_pair_url = f'{Config.CASEAPI_SERVICE}/uacqid/create'


@when('a UAC/QID pair is requested with a valid questionnaire type')
def generate_post_request_body(context):
    context.uacqid_json = {"questionnaireType":"01"}
    headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
    context.response = requests.post(url=caseapi_uacqid_pair_url, data=json.dumps(context.uacqid_json), headers=headers)


@then('caseapi should return a new UAC and QID with correct questionnaire type')
def generate_uacqid_pair(context):
    assert context.response.status_code == 201
    response_data = json.loads(context.response.content)
    assert 'uac' in response_data, 'uac missing in response'
    assert 'qid' in response_data, 'qid missing in response'
    assert context.uacqid_json["questionnaireType"] == response_data['qid'][:2]
