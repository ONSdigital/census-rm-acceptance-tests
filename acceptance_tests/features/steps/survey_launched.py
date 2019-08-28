import json

from behave import step

from acceptance_tests.features.steps.event_log import check_if_event_list_is_exact_match
from acceptance_tests.utilities.rabbit_context import RabbitContext
from config import Config


@step("a survey launched for a created case is received")
def create_survey_launch_event(context):
    context.survey_launched_case_id = context.uac_created_events[0]['payload']['uac']['caseId']
    questionnaire_id = context.uac_created_events[0]['payload']['uac']['questionnaireId']

    message = json.dumps(
        {
            "event": {
                "type": "SURVEY_LAUNCHED",
                "source": "CONTACT_CENTRE_API",
                "channel": "CC",
                "dateTime": "2011-08-12T20:17:46.384Z",
                "transactionId": "c45de4dc-3c3b-11e9-b210-d663bd873d93"
            },
            "payload": {
                "response": {
                    "questionnaireId": questionnaire_id,
                    "caseId": context.survey_launched_case_id,
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


@step("the events logged for the survey launched case are {expected_event_list}")
def check_survey_launch_event_logging(context, expected_event_list):
    check_if_event_list_is_exact_match(expected_event_list, context.survey_launched_case_id)
