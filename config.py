import os


class Config:
    SECURITY_USER_NAME = os.getenv('SECURITY_USER_NAME', 'admin')
    SECURITY_USER_PASSWORD = os.getenv('SECURITY_USER_PASSWORD', 'secret')
    BASIC_AUTH = (SECURITY_USER_NAME, SECURITY_USER_PASSWORD)

    PROTOCOL = os.getenv('PROTOCOL', 'http')

    ACTION_SERVICE_HOST = os.getenv('ACTION_SERVICE_HOST', 'localhost')
    ACTION_SERVICE_PORT = os.getenv('ACTION_SERVICE_PORT', '8301')
    ACTION_SERVICE = f'{PROTOCOL}://{ACTION_SERVICE_HOST}:{ACTION_SERVICE_PORT}'

    CASEAPI_SERVICE_HOST = os.getenv('CASEAPI_SERVICE_HOST', 'localhost')
    CASEAPI_SERVICE_PORT = os.getenv('CASEAPI_SERVICE_PORT', '8161')
    CASEAPI_SERVICE = f'{PROTOCOL}://{CASEAPI_SERVICE_HOST}:{CASEAPI_SERVICE_PORT}'

    RABBITMQ_HOST = os.getenv('RABBITMQ_SERVICE_HOST', 'localhost')
    RABBITMQ_PORT = os.getenv('RABBITMQ_SERVICE_PORT', '6672')
    RABBITMQ_VHOST = os.getenv('RABBITMQ_VHOST', '/')
    RABBITMQ_SAMPLE_INBOUND_QUEUE = os.getenv('RABBITMQ_QUEUE', 'case.sample.inbound')
    RABBITMQ_RH_OUTBOUND_CASE_QUEUE = os.getenv('RABBITMQ_RH_OUTBOUND_CASE_QUEUE', 'case.rh.case')
    RABBITMQ_RH_OUTBOUND_UAC_QUEUE = os.getenv('RABBITMQ_RH_OUTBOUND_UAC_QUEUE', 'case.rh.uac')
    RABBITMQ_UNADDRESSED_REQUEST_QUEUE = os.getenv('RABBITMQ_UNADDRESSED_REQUEST_QUEUE', 'unaddressedRequestQueue')
    RABBITMQ_QUESTIONNAIRE_LINKED_QUEUE = os.getenv('RABBITMQ_QUESTIONNAIRE_LINKED_QUEUE', 'case.questionnairelinked')
    RABBITMQ_OUTBOUND_FIELD_QUEUE = os.getenv('RABBITMQ_OUTBOUND_FIELD_QUEUE', 'Action.Field')
    RABBITMQ_INBOUND_EQ_QUEUE = os.getenv('RABBITMQ_INBOUND_EQ_QUEUE', 'Case.Responses')
    RABBITMQ_EVENT_EXCHANGE = os.getenv('RABBITMQ_EVENT_EXCHANGE', 'events')
    RABBITMQ_REFUSAL_ROUTING_KEY = os.getenv('RABBITMQ_REFUSAL_ROUTING_KEY', 'event.respondent.refusal')
    RABBITMQ_FULFILMENT_REQUESTED_ROUTING_KEY = os.getenv('RABBITMQ_FULFILMENT_REQUESTED_ROUTING_KEY',
                                                          'event.fulfilment.request')
    RABBITMQ_EXCHANGE = os.getenv('RABBITMQ_EXCHANGE', '')
    RABBITMQ_USER = os.getenv('RABBITMQ_USER', 'guest')
    RABBITMQ_PASSWORD = os.getenv('RABBITMQ_PASSWORD', 'guest')

    SFTP_HOST = os.getenv('SFTP_HOST', 'localhost')
    SFTP_PORT = os.getenv('SFTP_PORT', '122')
    SFTP_USERNAME = os.getenv('SFTP_USERNAME', 'centos')
    SFTP_KEY_FILENAME = os.getenv('SFTP_KEY_FILENAME', 'dummy_sftp_private_key')
    SFTP_KEY = os.getenv('SFTP_KEY', None)
    SFTP_PASSPHRASE = os.getenv('SFTP_PASSPHRASE', 'secret')
    SFTP_PPO_DIRECTORY = os.getenv('SFTP_PPO_DIRECTORY', 'ppo_dev/print_services/')
    SFTP_QM_DIRECTORY = os.getenv('SFTP_QM_DIRECTORY', 'qmprint_dev/print_services/')

    RECEIPT_TOPIC_PROJECT = os.getenv('RECEIPT_TOPIC_PROJECT', 'project')
    OFFLINE_RECEIPT_TOPIC_PROJECT = os.getenv('OFFLINE_RECEIPT_TOPIC_PROJECT', 'offline-project')
    RECEIPT_TOPIC_ID = os.getenv('RECEIPT_TOPIC_ID', 'eq-submission-topic')
    OFFLINE_RECEIPT_TOPIC_ID = os.getenv('OFFLINE_RECEIPT_TOPIC_ID', 'offline-receipting-topic')

    GOOGLE_APPLICATION_CREDENTIALS = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    GOOGLE_SERVICE_ACCOUNT_JSON = os.getenv('GOOGLE_SERVICE_ACCOUNT_JSON')

    # For test queues
    RABBITMQ_RH_OUTBOUND_CASE_QUEUE_TEST = 'case.rh.case.test'
    RABBITMQ_CASE_TEST_ROUTE = os.getenv('RH_CASE_ROUTING_KEY', 'event.case.*')
    RABBITMQ_RH_OUTBOUND_UAC_QUEUE_TEST = 'case.rh.uac.test'
    RABBITMQ_UAC_TEST_ROUTE = os.getenv('RH_UAC_ROUTING_KEY', "event.uac.*")
    RABBITMQ_RH_EXCHANGE_NAME = os.getenv('RH_EXCHANGE_NAME', "events")
    RABBITMQ_OUTBOUND_FIELD_QUEUE_TEST = 'RM.Field.Test'
    RABBITMQ_INBOUND_REFUSAL_QUEUE = 'case.refusals'
    RABBITMQ_INBOUND_FULFILMENT_REQUEST_QUEUE = 'case.fulfilments'
    RABBITMQ_INBOUND_NOTIFY_FULFILMENT_REQUEST_QUEUE = 'notify.fulfilments'
    RABBITMQ_OUTBOUND_ADAPTER_EXCHANGE = os.getenv('RABBITMQ_OUTBOUND_ADAPTER_EXCHANGE', 'adapter-outbound-exchange')

    NOTIFY_STUB_HOST = os.getenv('NOTIFY_STUB_HOST', 'localhost')
    NOTIFY_STUB_PORT = os.getenv('NOTIFY_STUB_PORT', '8917')
    NOTIFY_STUB_SERVICE = f'{PROTOCOL}://{NOTIFY_STUB_HOST}:{NOTIFY_STUB_PORT}'
