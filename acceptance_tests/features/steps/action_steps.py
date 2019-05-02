import uuid
from datetime import datetime, timedelta

from behave import given

from acceptance_tests.controllers.action_controller import create_action_plan, create_action_rule


@given('an action rule of type {action_type} is set {action_rule_delay} seconds in the future')
def setup_action_rule(context, action_type, action_rule_delay):
    action_plan_response_body = create_action_plan(context.action_plan_id)

    action_plan_url = action_plan_response_body['_links']['self']['href']

    trigger_date_time = (datetime.utcnow() + timedelta(seconds=int(action_rule_delay))).isoformat() + 'Z'
    classifiers = {'treatmentCode': ['HH_LF3R2E', 'HH_LF3R3AE', 'HH_LF3R3BE', 'HH_LFNR1E', 'HH_LF2R3BE']}

    create_action_rule(str(uuid.uuid4()), trigger_date_time, classifiers, action_plan_url, action_type)
