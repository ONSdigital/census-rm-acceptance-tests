import json
import time

from behave import step

from acceptance_tests.features.steps.event_log import check_if_event_list_is_exact_match
from acceptance_tests.utilities.database_helper import poll_database_query_with_timeout
from acceptance_tests.utilities.event_helper import check_survey_launched_case_updated_events
from acceptance_tests.utilities.rabbit_context import RabbitContext
from acceptance_tests.utilities.test_case_helper import test_helper
from config import Config


@step("a survey launched for a created case is received")
def create_survey_launch_event(context):
    context.survey_launched_case_id = context.uac_created_events[0]['payload']['uac']['caseId']
    questionnaire_id = context.uac_created_events[0]['payload']['uac']['questionnaireId']
    send_survey_launched_msg(context.survey_launched_case_id, questionnaire_id)


@step("the events logged for the survey launched case are {expected_event_list}")
def check_survey_launch_event_logging(context, expected_event_list):
    check_if_event_list_is_exact_match(expected_event_list, context.survey_launched_case_id)


def send_survey_launched_msg(case_id, qid, source="CONTACT_CENTRE_API", channel="CC"):
    message = json.dumps(
        {
            "event": {
                "type": "SURVEY_LAUNCHED",
                "source": source,
                "channel": channel,
                "dateTime": "2011-08-12T20:17:46.384Z",
                "transactionId": "c45de4dc-3c3b-11e9-b210-d663bd873d93"
            },
            "payload": {
                "response": {
                    "questionnaireId": qid,
                    "caseId": case_id,
                    "agentId": "cc_000351"
                }
            }
        }
    )

    with RabbitContext(exchange=Config.RABBITMQ_EVENT_EXCHANGE) as rabbit:
        rabbit.publish_message(
            message=message,
            content_type='application/json',
            routing_key=Config.RABBITMQ_SURVEY_LAUNCHED_ROUTING_KEY)


def check_survey_launches_in_action_db(case_ids):
    query = '''SELECT case_id, survey_launched FROM actionv2.cases WHERE case_id IN %s;'''
    query_vars = (tuple(case_ids),)

    def success_callback(db_result, timeout_deadline):
        results = {row[0]: row[1] for row in db_result}
        if all(results.values()) and len(results) == len(case_ids):
            return True
        elif time.time() > timeout_deadline:
            test_helper.fail(f"The expected cases did not all show as survey_launched=True within the time limit, "
                             f"found values: {results}")
        return False

    poll_database_query_with_timeout(query, query_vars, success_callback)


@step("a survey launched for a created case is received for cases with lsoa {lsoa_list}")
def send_survey_for_case_with_lsoa(context, lsoa_list):
    lsoas_to_match = lsoa_list.replace('[', '').replace(']', '').split(',')

    context.survey_started_case_ids = [
        case['payload']['collectionCase']['id']
        for case in context.case_created_events
        if case['payload']['collectionCase']['lsoa'] in lsoas_to_match
    ]

    for uac_created_event in context.uac_created_events:
        if uac_created_event['payload']['uac']['caseId'] in context.survey_started_case_ids:
            send_survey_launched_msg(uac_created_event['payload']['uac']['caseId'],
                                     uac_created_event['payload']['uac']['questionnaireId'], "RESPONDENT_HOME", "RH")

    check_survey_launched_case_updated_events(context, context.survey_started_case_ids)
    check_survey_launches_in_action_db(context.survey_started_case_ids)
