import uuid
from datetime import datetime, timedelta

from behave import given

from acceptance_tests.controllers.action_controller import create_action_plan, create_action_rule


@given('an action rule of type {action_type} is set {action_rule_delay} seconds in the future')
def setup_action_rule(context, action_type, action_rule_delay):
    action_plan_response_body = create_action_plan(context.action_plan_id)

    action_plan_url = action_plan_response_body['_links']['self']['href']

    trigger_date_time = (datetime.utcnow() + timedelta(seconds=int(action_rule_delay))).isoformat() + 'Z'

    classifiers_for_action_type = {
        'ICL1E': {'treatmentCode': ['HH_LFNR1E', 'HH_LFNR2E', 'HH_LFNR3AE', 'HH_LF2R1E', 'HH_LF2R2E', 'HH_LF2R3AE',
                                    'HH_LF2R3BE', 'HH_LF3R1E', 'HH_LF3R2E', 'HH_LF3R3AE', 'HH_LF3R3BE']},
        'ICL2W': {'treatmentCode': ['HH_LFNR1W', 'HH_LFNR2W', 'HH_LFNR3AW', 'HH_LF2R1W', 'HH_LF2R2W', 'HH_LF2R3AW',
                                    'HH_LF2R3BW', 'HH_LF3R1W', 'HH_LF3R2W', 'HH_LF3R3AW', 'HH_LF3R3BW']},
        'ICL4E': {'treatmentCode': ['HH_1LSFN', 'HH_2LEFN']},
        'ICHHQE': {'treatmentCode': ['HH_QF2R1E', 'HH_QF2R2E', 'HH_QF2R3AE', 'HH_QF3R1E', 'HH_QF3R2E', 'HH_QF3R3AE']},
        'ICHHQW': {'treatmentCode': ['HH_QF2R1W', 'HH_QF2R2W', 'HH_QF2R3AW', 'HH_QF3R1W', 'HH_QF3R2W', 'HH_QF3R3AW']},
        'ICHHQN': {'treatmentCode': ['HH_3QSFN']},
        'FF2QE': {'treatmentCode': ['HH_QF2R1E']}
    }

    create_action_rule(str(uuid.uuid4()), trigger_date_time, classifiers_for_action_type[action_type],
                       action_plan_url, action_type)
