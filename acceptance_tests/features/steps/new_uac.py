import functools
from behave import step

from acceptance_tests.utilities.rabbit_helper import start_listening_to_rabbit_queue, \
    store_all_uac_updated_msgs_by_collection_exercise_id
from acceptance_tests.utilities.test_case_helper import test_helper
from config import Config

questionnaire_type_to_form_type_map = {"01": "H", "02": "H", "03": "H", "04": "H",
                                       "11": None, "12": None, "13": None, "14": None,
                                       "21": "I", "22": "I", "23": "I", "24": "I",
                                       "31": "C", "32": "C", "33": "C", "34": "C",
                                       "41": None, "42": None, "43": None, "44": None,
                                       "51": "H", "52": "H", "53": "H", "54": "H",
                                       "61": None, "62": None, "63": None, "64": None,
                                       "71": "H", "72": "H", "73": "H", "74": "H",
                                       "81": "C", "82": "C", "83": "C", "84": "C"}


@step('a UAC updated message with "{questionnaire_type}" questionnaire type is emitted for the individual case')
def listen_for_ad_hoc_individual_uac_updated_message(context, questionnaire_type):
    check_qid_emitted_for_case(context, questionnaire_type, context.individual_case_id)


def check_qid_emitted_for_case(context, questionnaire_type, case_id):
    context.messages_received = []
    start_listening_to_rabbit_queue(Config.RABBITMQ_RH_OUTBOUND_UAC_QUEUE,
                                    functools.partial(store_all_uac_updated_msgs_by_collection_exercise_id,
                                                      context=context,
                                                      expected_msg_count=1,
                                                      collection_exercise_id=context.collection_exercise_id))
    uac_updated_event = context.messages_received[0]
    test_helper.assertEqual(uac_updated_event['payload']['uac']['caseId'], case_id,
                            'Fulfilment request UAC updated event found with wrong case ID')
    test_helper.assertEqual(uac_updated_event['payload']['uac']['questionnaireId'][:2], questionnaire_type,
                            'Fulfilment request UAC updated event found with wrong questionnaire type')
    context.requested_uac = uac_updated_event['payload']['uac']['uac']
    context.requested_qid = uac_updated_event['payload']['uac']['questionnaireId']

    # Check that the moon is on a stick for anybody who can't implement project-wide business logic
    actual_questionnaire_type = uac_updated_event['payload']['uac']['questionnaireId'][:2]
    expected_form_type = questionnaire_type_to_form_type_map[actual_questionnaire_type]

    if expected_form_type:
        test_helper.assertEqual(uac_updated_event['payload']['uac']['formType'], expected_form_type,
                                "The moon is NOT on a stick to our satisfaction")
    else:
        test_helper.assertIsNone(uac_updated_event['payload']['uac'].get('formType'))


@step('two UAC updated messages with "{questionnaire_type}" questionnaire type are emitted')
def listen_for_two_ad_hoc_uac_updated_messages(context, questionnaire_type):
    context.messages_received = []
    start_listening_to_rabbit_queue(Config.RABBITMQ_RH_OUTBOUND_UAC_QUEUE,
                                    functools.partial(store_all_uac_updated_msgs_by_collection_exercise_id,
                                                      context=context,
                                                      expected_msg_count=2,
                                                      collection_exercise_id=context.collection_exercise_id))
    uac_updated_events = context.messages_received

    test_helper.assertEqual(len(uac_updated_events), len(context.print_cases),
                            'UAC Updated Events does not match number of Case Created Events')

    context.requested_uac_and_qid = []

    for uac in uac_updated_events:
        compare_case_and_uac(context, questionnaire_type, uac)


def compare_case_and_uac(context, questionnaire_type, uac):
    for caze in context.print_cases:
        if caze['id'] == uac['payload']['uac']['caseId']:
            test_helper.assertTrue(uac['payload']['uac']['questionnaireId'].startswith(questionnaire_type),
                                   'Fulfilment request UAC updated event found with wrong questionnaire type')
            context.requested_uac_and_qid.append({'qid': uac['payload']['uac']['questionnaireId'],
                                                  'uac': uac['payload']['uac']['uac'], 'case': caze})
