import functools
import json
import uuid

from behave import when, step

from acceptance_tests.utilities.pubsub_helper import publish_to_pubsub
from acceptance_tests.utilities.rabbit_helper import start_listening_to_rabbit_queue
from acceptance_tests.utilities.test_case_helper import test_helper
from config import Config


@when("an undelivered mail QM message is put on GCP pubsub")
def undelivered_qm_published_to_gcp_pubsub(context):
    context.first_case = context.case_created_events[0]['payload']['collectionCase']
    questionnaire_id = context.uac_created_events[0]['payload']['uac']['questionnaireId']
    _publish_qm_undelivered_mail(context, questionnaire_id=questionnaire_id)
    test_helper.assertTrue(context.sent_to_gcp)


@when("an undelivered mail PPO message is put on GCP pubsub")
def undelivered_ppo_published_to_gcp_pubsub(context):
    context.first_case = context.case_created_events[0]['payload']['collectionCase']
    case_ref = context.first_case['caseRef']
    _publish_ppo_undelivered_mail(context, case_ref=case_ref)
    test_helper.assertTrue(context.sent_to_gcp)


@step("an ActionRequest event is sent to field work management")
def action_request_event_sent_to_fwm(context):
    context.messages_received = []
    start_listening_to_rabbit_queue(Config.RABBITMQ_OUTBOUND_FIELD_QUEUE, functools.partial(
        _field_work_receipt_callback, context=context))

    test_helper.assertEqual(context.fwmt_emitted_case_id, context.first_case["id"])
    test_helper.assertEqual(context.addressType, 'HH')
    test_helper.assertEqual(context.fwmt_emitted_undelivered_flag, True)


def _field_work_receipt_callback(ch, method, _properties, body, context):
    action_instruction = json.loads(body)

    if not action_instruction['actionInstruction'] == 'UPDATE':
        ch.basic_nack(delivery_tag=method.delivery_tag)
        test_helper.fail(f'Unexpected message on {Config.RABBITMQ_OUTBOUND_FIELD_QUEUE} case queue. '
                         f'Got "{action_instruction["actionInstruction"]}", wanted "UPDATE"')

    context.addressType = action_instruction['addressType']
    context.fwmt_emitted_case_id = action_instruction['caseId']
    context.fwmt_emitted_undelivered_flag = action_instruction['undeliveredAsAddress']

    test_helper.assertEquals(context.first_case['address']['uprn'], action_instruction['uprn'], "uprn")
    test_helper.assertEquals(context.first_case['address']['estabUprn'], action_instruction['estabUprn'], "estab Uprn")

    ch.basic_ack(delivery_tag=method.delivery_tag)
    ch.stop_consuming()


def _publish_ppo_undelivered_mail(context, case_ref):
    context.sent_to_gcp = False

    data = json.dumps({"transactionId": str(uuid.uuid4()),
                       "dateTime": "2019-08-03T14:30:01",
                       "caseRef": case_ref,
                       "productCode": "P_OR_H1",
                       "channel": "PPO",
                       "type": "UNDELIVERED_MAIL_REPORTED",
                       "unreceipt": False})

    publish_to_pubsub(data, Config.PPO_UNDELIVERED_PROJECT_ID, Config.PPO_UNDELIVERED_TOPIC_NAME)

    context.sent_to_gcp = True


def _publish_qm_undelivered_mail(context, questionnaire_id):
    context.sent_to_gcp = False

    data = json.dumps({
        "transactionId": str(uuid.uuid4()),
        "dateTime": "2008-08-24T00:00:00",
        "questionnaireId": questionnaire_id,
        "unreceipt": False
    })

    publish_to_pubsub(data, Config.QM_UNDELIVERED_PROJECT_ID, Config.QM_UNDELIVERED_TOPIC_NAME)

    context.sent_to_gcp = True
