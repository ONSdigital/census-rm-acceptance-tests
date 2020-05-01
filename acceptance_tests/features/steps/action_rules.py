import json
import time
import uuid
from datetime import datetime

import psycopg2
import requests
from behave import step
from retrying import retry

from acceptance_tests.controllers.action_controller import create_action_plan, create_action_rule
from acceptance_tests.features.steps.case_look_up import get_logged_events_for_case_by_id
from acceptance_tests.utilities.test_case_helper import test_helper
from config import Config


@step('set action rule of type "{action_type}" when the case loading queues are drained')
def setup_print_action_rule_once_case_action_is_drained(context, action_type):
    poll_until_sample_is_ingested_to_action(context)
    # TODO these checks intermittently fail as the queue can occasionally be empty while being drained
    # the sleep is a temporary work around until this is fixed proper
    # (by checking for all the cases in the action scheduler DB)
    setup_treatment_code_classified_action_rule(context, action_type)


def poll_until_sample_is_ingested_to_action(context):
    sql_query = """SELECT count(*) FROM actionv2.cases WHERE action_plan_id = %s"""
    conn = psycopg2.connect(f"dbname='{Config.DB_NAME}' user={Config.DB_USERNAME} host='{Config.DB_HOST}' "
                            f"password={Config.DB_PASSWORD} port='{Config.DB_PORT}'{Config.DB_USESSL}")
    timeout = time.time() + 60
    cur = conn.cursor()
    while True:
        cur.execute(sql_query, (context.action_plan_id,))
        db_result = cur.fetchall()
        if db_result[0][0] == context.sample_count:
            return
        elif time.time() > timeout:
            test_helper.fail(
                f'For Action-plan {context.action_plan_id}, DB didn\'t have the expected number of sample units. '
                f'Expected: {context.sample_count}, actual: {db_result[0][0]}')
        time.sleep(1)


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
                                           'HH_QFNR1E']},
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
        'SPG_IC11': {'treatment_code': ['SPG_LPHUE']},
        'SPG_IC12': {'treatment_code': ['SPG_LPHUW']},
        'P_RD_2RL1_1': {'lsoa': ['E01014540', 'E01014541', 'E01014542', 'W01014540']},
        'P_RD_2RL2B_1': {'lsoa': ['E01014669', 'W01014669']},
        'P_RD_2RL1_2': {'lsoa': ['E01014543', 'E01014544']},
        'P_RD_2RL2B_2': {'lsoa': ['E01033361', 'E01015005', 'W01033361', 'W01015005']},
        'P_RD_2RL1_3': {'lsoa': ['E01014545']},
        'P_RD_2RL2B_3': {'lsoa': ['E01014897', 'W01014897']}
    }

    build_and_create_action_rule(context, classifiers_for_action_type[action_type], action_type)


@step('a FIELD action rule for address type "{address_type}" is set when loading queues are drained')
def create_field_action_plan(context, address_type):
    poll_until_sample_is_ingested_to_action(context)
    build_and_create_action_rule(context, {'address_type': [address_type]}, 'FIELD')


def build_and_create_action_rule(context, classifier, action_type):
    action_plan_response_body = create_action_plan(context.action_plan_id)
    action_plan_url = action_plan_response_body['_links']['self']['href']
    trigger_date_time = datetime.utcnow().isoformat() + 'Z'

    create_action_rule(str(uuid.uuid4()), trigger_date_time, classifier,
                       action_plan_url, action_type)


def _wait_for_queue_to_be_drained(queue_name):
    while True:
        if get_msg_count(queue_name) == 0:
            return

        time.sleep(0.1)


def get_msg_count(queue_name):
    uri = f'http://{Config.RABBITMQ_HOST}:{Config.RABBITMQ_HTTP_PORT}/api/queues/%2f/{queue_name}'
    response = requests.get(uri, auth=(Config.RABBITMQ_USER, Config.RABBITMQ_PASSWORD))
    response.raise_for_status()
    response_data = json.loads(response.content)

    return response_data['messages']


@step('set action rule of type "{action_type}" when case event "{event_type}" is logged')
def set_action_rule_when_case_event_logged(context, action_type, event_type):
    check_for_event(context, event_type)
    setup_treatment_code_classified_action_rule(context, action_type)


@retry(stop_max_attempt_number=30, wait_fixed=1000)
def check_for_event(context, event_type):
    events = get_logged_events_for_case_by_id(context.case_created_events[0]['payload']['collectionCase']['id'])

    for event in events:
        if event['eventType'] == event_type:
            return

    test_helper.fail(f"Case {context.first_case['id']} event_type {event_type} not logged")
