import json

import luhn

from acceptance_tests.utilities.test_case_helper import test_helper
from config import Config


def fieldwork_create_message_callback(ch, method, _properties, body, context):
    action_instruction = json.loads(body)

    if not action_instruction['actionInstruction'] == 'CREATE':
        ch.basic_nack(delivery_tag=method.delivery_tag)
        test_helper.fail(f'Unexpected message on {Config.RABBITMQ_OUTBOUND_FIELD_QUEUE} case queue. '
                         f'Got "{action_instruction["actionInstruction"]}", wanted "CREATE"')

    for index, case in enumerate(context.expected_cases_for_action):
        if _message_matches(case, action_instruction):
            _message_valid(case, action_instruction)
            del context.expected_cases_for_action[index]
            ch.basic_ack(delivery_tag=method.delivery_tag)

            break
    else:
        test_helper.fail(
            f'Found message on {Config.RABBITMQ_OUTBOUND_FIELD_QUEUE} case queue which did not '
            f'match any expected sample units')

    if not context.expected_cases_for_action:
        ch.stop_consuming()


def _message_matches(case, action_instruction):
    return action_instruction['caseId'] == case['id']


def _message_valid(case, action_instruction):
    test_helper.assertEqual(float(case['address']['latitude']), action_instruction['latitude'])
    test_helper.assertEqual(float(case['address']['longitude']), action_instruction['longitude'])
    test_helper.assertEqual(case['address']['postcode'], action_instruction['postcode'])
    test_helper.assertEqual('CENSUS', action_instruction['surveyName'])
    test_helper.assertEqual(case['address']['estabType'], action_instruction['estabType'])
    test_helper.assertEquals(case['ceExpectedCapacity'], int(action_instruction['ceExpectedCapacity']))
    test_helper.assertEquals(case['ceActualResponses'], int(action_instruction['ceActualResponses']))
    test_helper.assertEquals(case['handDelivery'], action_instruction['handDeliver'])
    test_helper.assertEquals(case['caseRef'], action_instruction['caseRef'])
    test_helper.assertEquals(len(action_instruction['caseRef']), 10)
    test_helper.assertEquals(case['address']['uprn'], action_instruction['uprn'])
    test_helper.assertEquals(case['address']['estabUprn'], action_instruction['estabUprn'])
    test_helper.assertTrue(luhn.verify(action_instruction['caseRef']))


def field_work_cancel_callback(ch, method, _properties, body, context):
    action_cancel = json.loads(body)

    if not action_cancel['actionInstruction'] == 'CANCEL':
        ch.basic_nack(delivery_tag=method.delivery_tag)
        test_helper.fail(f'Unexpected message on {Config.RABBITMQ_OUTBOUND_FIELD_QUEUE} case queue. '
                         f'Got "{action_cancel["actionInstruction"]}", wanted "CANCEL"')

    context.addressType = action_cancel['addressType']
    context.fwmt_emitted_case_id = action_cancel['caseId']
    context.field_action_cancel_message = action_cancel
    ch.basic_ack(delivery_tag=method.delivery_tag)
    ch.stop_consuming()


def field_work_update_callback_without_faff(ch, method, _properties, body, context):
    action_cancel = json.loads(body)

    if not action_cancel['actionInstruction'] == 'UPDATE':
        ch.basic_nack(delivery_tag=method.delivery_tag)
        test_helper.fail(f'Unexpected message on {Config.RABBITMQ_OUTBOUND_FIELD_QUEUE} case queue. '
                         f'Got "{action_cancel["actionInstruction"]}", wanted "UPDATE"')

    context.addressType = action_cancel['addressType']
    context.fwmt_emitted_case_id = action_cancel['caseId']
    context.field_action_cancel_message = action_cancel
    ch.basic_ack(delivery_tag=method.delivery_tag)
    ch.stop_consuming()


def field_work_update_callback(ch, method, _properties, body, context):
    action_instruction = json.loads(body)

    if not action_instruction['actionInstruction'] == 'UPDATE':
        ch.basic_nack(delivery_tag=method.delivery_tag)
        test_helper.fail(f'Unexpected message on {Config.RABBITMQ_OUTBOUND_FIELD_QUEUE} case queue. '
                         f'Got "{action_instruction["actionInstruction"]}", wanted "UPDATE"')

    for index, case in enumerate(context.expected_cases_for_action):
        if _message_matches(case, action_instruction):
            del context.expected_cases_for_action[index]
            ch.basic_ack(delivery_tag=method.delivery_tag)

            break
    else:
        test_helper.fail(
            f'Found message on {Config.RABBITMQ_OUTBOUND_FIELD_QUEUE} case queue which did not '
            f'match any expected sample units')

    if not context.expected_cases_for_action:
        ch.stop_consuming()
