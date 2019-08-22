import json

from behave import step

from acceptance_tests.utilities.rabbit_context import RabbitContext
from config import Config


@step("an invalid address message is sent")
def invalid_address_message(context):
    context.emitted_case = context.case_created_events[0]['payload']['collectionCase']

    message = json.dumps(
        {
            "event": {
                "type": "ADDRESS_NOT_VALID",
                "source": "FIELDWORK_GATEWAY",
                "channel": "FIELD",
                "dateTime": "2019-07-07T22:37:11.988+0000",
                "transactionId": "d2541acb-230a-4ade-8123-eee2310c9143"
            },
            "payload": {
                "invalidAddress": {
                    "reason": "DEMOLISHED",
                    "collectionCase": {
                        "id": context.emitted_case['id']
                    }
                }
            }
        }
    )

    with RabbitContext(exchange=Config.RABBITMQ_EVENT_EXCHANGE) as rabbit:
        rabbit.publish_message(
            message=message,
            content_type='application/json',
            routing_key=Config.RABBITMQ_INVALID_ADDRESS_ROUTING_KEY)
