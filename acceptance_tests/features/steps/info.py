from behave import *
import requests

from acceptance_tests.config import Config


@given('we have rm services running')
def services_running(context):
    pass


@when('we call info endpoint')
def setup_get_request_info(context):
    pass


@then('we get 200 response')
def get_request_info(context):
    action_service_info_endpoint = f'{Config.ACTION_SERVICE}/info'
    r = requests.get(action_service_info_endpoint)
    assert r.status_code == 200


