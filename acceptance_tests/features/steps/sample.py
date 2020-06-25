from behave import step


from acceptance_tests.features.steps.action_rules import poll_until_sample_is_ingested_to_action
from acceptance_tests.utilities.event_helper import get_and_check_case_created_messages, \
    get_and_check_uac_updated_messages
from acceptance_tests.utilities.sample_load_helper import load_sample_file_helper


@step('sample file "{sample_file_name}" is loaded')
def load_sample_file_step(context, sample_file_name):
    load_sample_file_helper(context, sample_file_name)


@step('sample file "{sample_file_name}" is loaded successfully with census action plan collection ids')
def load_sample_file_successfully_with_census_action_plan_collection_ids(context, sample_file_name):
    load_sample_file_successfully_step(context, sample_file_name, check_loaded_into_db=False)


@step('sample file "{sample_file_name}" is loaded successfully')
def load_sample_file_successfully_step(context, sample_file_name, check_loaded_into_db=True):
    load_sample_file_helper(context, sample_file_name)

    get_and_check_case_created_messages(context)
    get_and_check_uac_updated_messages(context)

    if check_loaded_into_db:
        poll_until_sample_is_ingested_to_action(context)

    context.first_case = context.case_created_events[0]['payload']['collectionCase']
    context.loaded_case = context.case_created_events[0]['payload']['collectionCase']
    context.receipting_case = context.case_created_events[0]['payload']['collectionCase']
    context.qid_to_receipt = context.uac_created_events[0]['payload']['uac']['questionnaireId']
