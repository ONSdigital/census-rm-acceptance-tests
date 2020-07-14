from datetime import datetime

import time
from behave import step

from acceptance_tests.utilities.action_helper import poll_until_sample_is_ingested_to_action
from acceptance_tests.utilities.event_helper import get_and_check_sample_load_case_created_messages, \
    get_and_check_uac_updated_messages, get_and_test_case_and_uac_msgs_are_correct
from acceptance_tests.utilities.sample_load_helper import load_sample_file_helper


@step('sample file "{sample_file_name}" is loaded')
def load_sample_file_step(context, sample_file_name):
    load_sample_file_helper(context, sample_file_name)


@step('sample file "{sample_file_name}" is loaded successfully')
def load_sample_file_successfully_step(context, sample_file_name):
    load_sample_file_helper(context, sample_file_name)

    get_and_check_sample_load_case_created_messages(context)
    get_and_check_uac_updated_messages(context)

    poll_until_sample_is_ingested_to_action(context)

    context.first_case = context.case_created_events[0]['payload']['collectionCase']
    context.loaded_case = context.case_created_events[0]['payload']['collectionCase']
    context.receipting_case = context.case_created_events[0]['payload']['collectionCase']
    context.qid_to_receipt = context.uac_created_events[0]['payload']['uac']['questionnaireId']


@step('sample file "{sample_file_name}" is loaded and correct qids {questionnaire_types} set')
def load_sample_file_and_check_qids(context, sample_file_name, questionnaire_types):
    load_sample_file_helper(context, sample_file_name)
    get_and_test_case_and_uac_msgs_are_correct(context, questionnaire_types)


@step('{wait:d} second later delta sample file "{sample_file_name}" is loaded successfully')
def load_sample_file_successfully_after(context, wait, sample_file_name):
    # Remove initial sample load cases/uacs from the context
    context.case_created_events = []
    context.uac_created_events = []

    time.sleep(wait)
    context.address_delta_load_time = datetime.utcnow()

    load_sample_file_helper(context, sample_file_name)
    get_and_check_sample_load_case_created_messages(context)
    get_and_check_uac_updated_messages(context)

    poll_until_sample_is_ingested_to_action(context, after_date_time=context.address_delta_load_time)
