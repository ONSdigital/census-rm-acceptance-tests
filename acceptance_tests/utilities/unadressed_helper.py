import functools
import json

from acceptance_tests.utilities.rabbit_context import RabbitContext
from acceptance_tests.utilities.rabbit_helper import start_listening_to_rabbit_queue
from acceptance_tests.utilities.test_case_helper import test_helper
from config import Config


def send_questionnaire_linked_msg_to_rabbit(questionnaire_id, case_id):
    questionnaire_linked_message = {
        'event': {
            'type': 'QUESTIONNAIRE_LINKED',
            'source': 'FIELDWORK_GATEWAY',
            'channel': 'FIELD',
            "dateTime": "2011-08-12T20:17:46.384Z",
            "transactionId": "c45de4dc-3c3b-11e9-b210-d663bd873d93"
        },
        'payload': {
            'uac': {
                "caseId": case_id,
                'questionnaireId': questionnaire_id,
            }
        }
    }
    with RabbitContext(exchange=Config.RABBITMQ_EVENT_EXCHANGE) as rabbit:
        rabbit.publish_message(
            message=json.dumps(questionnaire_linked_message),
            content_type='application/json',
            routing_key=Config.RABBITMQ_QUESTIONNAIRE_LINKED_ROUTING_KEY)


def check_uac_message_is_received(context):
    context.messages_received = []
    context.expected_message_received = False
    start_listening_to_rabbit_queue(Config.RABBITMQ_RH_OUTBOUND_UAC_QUEUE,
                                    functools.partial(_uac_callback, context=context))

    test_helper.assertTrue(context.expected_message_received)
    context.uac_message_received = context.messages_received[0]


def _uac_callback(ch, method, _properties, body, context):
    parsed_body = json.loads(body)

    if not parsed_body['event']['type'] == 'UAC_UPDATED':
        ch.basic_nack(delivery_tag=method.delivery_tag)
        return

    test_helper.assertEqual(64, len(parsed_body['payload']['uac']['uacHash']))
    context.expected_questionnaire_id = parsed_body['payload']['uac']['questionnaireId']
    test_helper.assertEqual(context.expected_questionnaire_type, context.expected_questionnaire_id[:2])
    context.expected_uac = parsed_body['payload']['uac']['uac']
    context.expected_message_received = True
    context.messages_received.append(parsed_body)
    ch.basic_ack(delivery_tag=method.delivery_tag)
    ch.stop_consuming()
