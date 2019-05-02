from collections import defaultdict


def create_expected_csv_lines(context, prefix):
    actual_data = defaultdict(dict)

    for message in context.messages_received:
        if message['event']['type'] == 'UAC_UPDATED':
            actual_data[message['payload']['uac']['caseId']]['uac'] = message['payload']['uac']['uac']
        elif message['event']['type'] == 'CASE_CREATED':
            actual_data[message['payload']['collectionCase']['id']]['case_ref'] = message['payload']['collectionCase'][
                'caseRef']
            actual_data[message['payload']['collectionCase']['id']]['address_line_1'] = \
                message['payload']['collectionCase']['address']['addressLine1']
            actual_data[message['payload']['collectionCase']['id']]['address_line_2'] = \
                message['payload']['collectionCase']['address']['addressLine2']
            actual_data[message['payload']['collectionCase']['id']]['address_line_3'] = \
                message['payload']['collectionCase']['address']['addressLine3']
            actual_data[message['payload']['collectionCase']['id']]['town_name'] = \
                message['payload']['collectionCase']['address']['townName']
            actual_data[message['payload']['collectionCase']['id']]['postcode'] = \
                message['payload']['collectionCase']['address']['postcode']

    return [
        _create_expected_csv_line(case, prefix)
        for case in actual_data.values()
    ]


def _create_expected_csv_line(case, prefix):
    return (
        f'{case["uac"]}|'
        f'{case["case_ref"]}|'
        f'{case["address_line_1"]}|'
        f'{case["address_line_2"]}|'
        f'{case["address_line_3"]}|'
        f'{case["town_name"]}|'
        f'{case["postcode"]}|'
        f'{prefix}'
    )
