from behave import *
import requests


@given('we have rm services running')
def services_running(context):
    pass


@when('we call info endpoint')
def setup_get_request_info(context):
    pass


@then('we get 200 response')
def get_request_info(context):
    r = requests.get('http://localhost:8151/info')
    assert r.status_code == 200


