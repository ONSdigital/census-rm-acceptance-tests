import uuid
from datetime import datetime, timedelta

from behave import given, step

from acceptance_tests.controllers.action_controller import create_action_plan, create_action_rule


@given('an action rule of type "{action_type}" is set {action_rule_delay} seconds in the future')
def setup_action_rule(context, action_type, action_rule_delay):
    classifiers_for_action_type = {
        'ICL1E': {'treatment_code': ['HH_LFNR1E', 'HH_LFNR2E', 'HH_LFNR3AE', 'HH_LF2R1E', 'HH_LF2R2E', 'HH_LF2R3AE',
                                     'HH_LF2R3BE', 'HH_LF3R1E', 'HH_LF3R2E', 'HH_LF3R3AE', 'HH_LF3R3BE']},
        'ICL2W': {'treatment_code': ['HH_LFNR1W', 'HH_LFNR2W', 'HH_LFNR3AW', 'HH_LF2R1W', 'HH_LF2R2W', 'HH_LF2R3AW',
                                     'HH_LF2R3BW', 'HH_LF3R1W', 'HH_LF3R2W', 'HH_LF3R3AW', 'HH_LF3R3BW']},
        'ICL4N': {'treatment_code': ['HH_1LSFN', 'HH_2LEFN']},
        'ICHHQE': {'treatment_code': ['HH_QF2R1E', 'HH_QF2R2E', 'HH_QF2R3AE', 'HH_QF3R1E', 'HH_QF3R2E', 'HH_QF3R3AE']},
        'ICHHQW': {'treatment_code': ['HH_QF2R1W', 'HH_QF2R2W', 'HH_QF2R3AW', 'HH_QF3R1W', 'HH_QF3R2W', 'HH_QF3R3AW']},
        'ICHHQN': {'treatment_code': ['HH_3QSFN']},
        'FIELD': {'treatment_code': ['HH_QF2R1E']},

        'P_RL_1RL1_1': {'treatment_code': ['HH_LF2R1E', 'HH_LF3R1E', 'HH_LFNR1E', 'HH_QF2R1E', 'HH_QF3R1E',
                                           'HH_QFNR1E']},
        'P_RL_2RL2B_3a': {'treatment_code': ['HH_LF2R3AW', 'HH_LF3R3AW', 'HH_LFNR3AW', 'HH_QF2R3AW', 'HH_QF3R3AW',
                                             'HH_QFNR3AW']},
        'P_QU_H2': {'treatment_code': ['HH_LF2R3BW', 'HH_LF3R3BW', 'HH_LFNR3BW']},
        'P_RD_2RL1_1': {'lsoa': ['E01014540', 'E01014541', 'E01014542']},
        'P_RD_2RL2B_1': {'lsoa': ['E01014669']},
        'P_RD_2RL1_2': {'lsoa': ['E01014543', 'E01014544']},
        'P_RD_2RL2B_2': {'lsoa': ['E01033361', 'E01015005']},
        'P_RD_2RL1_3': {'lsoa': ['E01014545']},
        'P_RD_2RL2B_3': {'lsoa': ['E01014897']}
    }

    build_and_create_action_rule(context, classifiers_for_action_type[action_type], action_type, action_rule_delay)


@step("an action rule for community estabs is set 5 seconds in the future")
def create_ce_action_plan(context):
    build_and_create_action_rule(context, {'address_type': ['CE']}, 'FIELD', 5)


def build_and_create_action_rule(context, classifier, action_type, action_rule_delay):
    action_plan_response_body = create_action_plan(context.action_plan_id)
    action_plan_url = action_plan_response_body['_links']['self']['href']
    trigger_date_time = (datetime.utcnow() + timedelta(seconds=int(action_rule_delay))).isoformat() + 'Z'

    create_action_rule(str(uuid.uuid4()), trigger_date_time, classifier,
                       action_plan_url, action_type)
