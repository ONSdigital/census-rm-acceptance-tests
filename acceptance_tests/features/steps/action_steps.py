import uuid
from datetime import datetime, timedelta

from behave import given

from acceptance_tests.controllers.action_controller import create_action_plan, create_action_rule


@given('an action rule of type {action_type} is set {action_rule_delay} seconds in the future')
def setup_action_rule(context, action_type, action_rule_delay):
    action_plan_response_body = create_action_plan(context.action_plan_id)

    action_plan_url = action_plan_response_body['_links']['self']['href']

    trigger_date_time = (datetime.utcnow() + timedelta(seconds=int(action_rule_delay))).isoformat() + 'Z'

    if action_type == 'ICL1E':
        classifiers = _get_england_icl_treatment_codes()

    if action_type == 'ICL2W':
        classifiers = _get_wales_icl_treatment_codes()

    if action_type == 'ICHHQW':
        classifiers = _get_wales_questionnaire_treatment_codes()

    create_action_rule(str(uuid.uuid4()), trigger_date_time, classifiers, action_plan_url, action_type)


def _get_england_icl_treatment_codes():
    return {'treatmentCode': ['HH_LF3R2E', 'HH_LF3R3AE', 'HH_LF3R3BE', 'HH_LFNR1E', 'HH_LF2R3BE']}


def _get_wales_icl_treatment_codes():
    return {'treatmentCode': ['HH_LFNR1W', 'HH_LFNR2W', 'HH_LFNR3AW', 'HH_LF2R1W', 'HH_LF2R2W', 'HH_LF2R3AW',
                              'HH_LF2R3BW', 'HH_LF3R1W', 'HH_LF3R2W', 'HH_LF3R3AW', 'HH_LF3R3BW']}


def _get_wales_questionnaire_treatment_codes():
    return {'treatmentCode': ['HH_QF2R1W', 'HH_QF2R2W', 'HH_QF2R3AW', 'HH_QF3R1W', 'HH_QF3R2W', 'HH_QF3R3AW']}
