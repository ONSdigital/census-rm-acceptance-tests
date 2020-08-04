import time
import uuid
from datetime import datetime

import requests

from acceptance_tests.utilities.database_helper import poll_database_query_with_timeout
from acceptance_tests.utilities.mappings import CLASSIFIERS_FOR_ACTION_TYPE, DEFAULT_CLASSIFIERS
from acceptance_tests.utilities.test_case_helper import test_helper
from config import Config


def poll_until_sample_is_ingested_to_action(context, after_date_time=None):
    if not after_date_time:
        after_date_time = context.test_start_utc
    query = "SELECT count(*) FROM actionv2.cases WHERE action_plan_id = %s AND created_date_time > %s"

    def success_callback(db_result, timeout_deadline):
        if db_result[0][0] == context.sample_count:
            return True
        elif time.time() > timeout_deadline:
            test_helper.fail(
                f"For Action-plan {context.action_plan_id}, DB didn't have the expected number of sample units. "
                f"Expected: {context.sample_count}, actual: {db_result[0][0]}")
        return False

    poll_database_query_with_timeout(query, (context.action_plan_id, after_date_time),
                                     success_callback)


def setup_classified_action_rule(context, action_type):
    build_and_create_action_rule(context, DEFAULT_CLASSIFIERS + CLASSIFIERS_FOR_ACTION_TYPE[action_type], action_type)


def setup_address_frame_delta_action_rule(context, action_type):
    classifiers = DEFAULT_CLASSIFIERS + CLASSIFIERS_FOR_ACTION_TYPE[action_type]
    classifiers += (f" AND created_date_time BETWEEN '{context.address_delta_load_time.isoformat()}'"
                    f" AND '{datetime.utcnow().isoformat()}'")
    build_and_create_action_rule(context, classifiers, action_type)


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
    body = {'id': action_rule_id, 'triggerDateTime': trigger_date_time, 'classifiersClause': classifiers,
            'actionPlan': action_plan_url, 'actionType': action_type, 'hasTriggered': has_triggered}

    response = requests.post(url, auth=Config.BASIC_AUTH, json=body)
    response.raise_for_status()

    return response.json()
