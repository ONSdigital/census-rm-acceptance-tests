import time
import uuid
from datetime import datetime

import requests

from acceptance_tests.utilities.database_helper import poll_database_query_with_timeout
from acceptance_tests.utilities.test_case_helper import test_helper
from config import Config


def poll_until_sample_is_ingested_to_action(context):
    sql_query = """SELECT count(*) FROM actionv2.cases WHERE action_plan_id = %s"""

    def success_callback(db_result, timeout_deadline):
        if db_result[0][0] == context.sample_count:
            return True
        elif time.time() > timeout_deadline:
            test_helper.fail(
                f"For Action-plan {context.action_plan_id}, DB didn't have the expected number of sample units. "
                f"Expected: {context.sample_count}, actual: {db_result[0][0]}")
        return False

    poll_database_query_with_timeout(sql_query, (context.action_plan_id,), success_callback)


def setup_treatment_code_classified_action_rule(context, action_type):
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
                                           'HH_QFNR1E'], 'survey_launched': ['f']},
        'P_RL_2RL2B_3a': {'treatment_code': ['HH_LF2R3AW', 'HH_LF3R3AW', 'HH_LFNR3AW', 'HH_QF2R3AW', 'HH_QF3R3AW',
                                             'HH_QFNR3AW']},
        'P_QU_H2': {'treatment_code': ['HH_LF2R3BW', 'HH_LF3R3BW', 'HH_LFNR3BW']},
        'CE1_IC01': {'treatment_code': ['CE_LDCEE']},
        'CE1_IC02': {'treatment_code': ['CE_LDCEW']},
        'CE_IC03': {'treatment_code': ['CE_LDIEE']},
        'CE_IC04': {'treatment_code': ['CE_LDIEW']},
        'CE_IC03_1': {'treatment_code': ['CE_LDIUE']},
        'CE_IC04_1': {'treatment_code': ['CE_LDIUW']},
        'CE_IC05': {'treatment_code': ['CE_2LNFN']},
        'CE_IC06': {'treatment_code': ['CE_3LSNFN']},
        'CE_IC08': {'treatment_code': ['CE_1QNFN']},
        'CE_IC09': {'treatment_code': ['CE_QDIEE']},
        'CE_IC10': {'treatment_code': ['CE_QDIEW']},
        'SPG_IC11': {'treatment_code': ['SPG_LPHUE']},
        'SPG_IC12': {'treatment_code': ['SPG_LPHUW']},
        'SPG_IC13': {'treatment_code': ['SPG_QDHUE']},
        'SPG_IC14': {'treatment_code': ['SPG_QDHUW']},
        'P_RD_2RL1_1': {'lsoa': ['E01014540', 'E01014541', 'E01014542', 'W01014540']},
        'P_RD_2RL2B_1': {'lsoa': ['E01014669', 'W01014669']},
        'P_RD_2RL1_2': {'lsoa': ['E01014543', 'E01014544']},
        'P_RD_2RL2B_2': {'lsoa': ['E01033361', 'E01015005', 'W01033361', 'W01015005']},
        'P_RD_2RL1_3': {'lsoa': ['E01014545']},
        'P_RD_2RL2B_3': {'lsoa': ['E01014897', 'W01014897']},

        'P_RL_1RL1A': {'lsoa': ['E01014540', 'E01014541', 'E01014542'], 'survey_launched': ['t']},
        'P_RL_1RL2BA': {'lsoa': ['E01014669', 'W01014669']},
        'P_RL_2RL1A': {'lsoa': ['E01014543', 'E01014544']},
        'P_RL_2RL2BA': {'lsoa': ['E01033361', 'E01015005', 'W01033361', 'W01015005']},
    }

    build_and_create_action_rule(context, classifiers_for_action_type[action_type], action_type)


def build_and_create_action_rule(context, classifier, action_type):
    action_plan_response_body = create_action_plan(context.action_plan_id)
    action_plan_url = action_plan_response_body['_links']['self']['href']
    trigger_date_time = datetime.utcnow().isoformat() + 'Z'

    create_action_rule(str(uuid.uuid4()), trigger_date_time, classifier,
                       action_plan_url, action_type)


def create_action_plan(action_plan_id):
    url = f'{Config.ACTION_SERVICE}/actionPlans'
    body = {'id': action_plan_id}
    response = requests.post(url, auth=Config.BASIC_AUTH, json=body)
    response.raise_for_status()

    return response.json()


def create_action_rule(action_rule_id, trigger_date_time, classifiers, action_plan_url, action_type,
                       has_triggered=False):
    url = f'{Config.ACTION_SERVICE}/actionRules'
    body = {'id': action_rule_id, 'triggerDateTime': trigger_date_time, 'classifiers': classifiers,
            'actionPlan': action_plan_url, 'actionType': action_type, 'hasTriggered': has_triggered}

    response = requests.post(url, auth=Config.BASIC_AUTH, json=body)
    response.raise_for_status()

    return response.json()
