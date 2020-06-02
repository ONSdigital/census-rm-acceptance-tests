import json

from behave import step

from acceptance_tests.utilities.rabbit_context import RabbitContext
from config import Config


@step('a Field Case Updated message has been sent with expected capacity as "{expected_capacity}"')
def send_field_case_updated_message(context, expected_capacity):
    case_id = context.first_case['id']
    message = json.dumps(
        {
            "event": {
                "type": "FIELD_CASE_UPDATED",
                "source": "FIELDWORK_GATEWAY",
                "channel": "FIELD",
                "dateTime": "2011-08-12T20:17:46.384Z",
                "transactionId": "c45de4dc-3c3b-11e9-b210-d663bd873d93"
            },
            "payload": {
                "collectionCase": {
                    "id": case_id,
                    "ceExpectedCapacity": expected_capacity
                }
            }
        })
    with RabbitContext(exchange=Config.RABBITMQ_EVENT_EXCHANGE) as rabbit:
        rabbit.publish_message(
            message=message,
            content_type='application/json',
            routing_key=Config.RABBITMQ_FIELD_CASE_UPDATED_ROUTING_KEY)