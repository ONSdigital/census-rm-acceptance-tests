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
    RABBITMQ_HTTP_PORT = os.getenv('RABBITMQ_HTTP_PORT', '16672')
    RABBITMQ_VHOST = os.getenv('RABBITMQ_VHOST', '/')
    RABBITMQ_SAMPLE_INBOUND_QUEUE = os.getenv('RABBITMQ_QUEUE', 'case.sample.inbound')
    RABBITMQ_RH_OUTBOUND_CASE_QUEUE = os.getenv('RABBITMQ_RH_OUTBOUND_CASE_QUEUE', 'case.rh.case')
    RABBITMQ_RH_OUTBOUND_UAC_QUEUE = os.getenv('RABBITMQ_RH_OUTBOUND_UAC_QUEUE', 'case.rh.uac')
    RABBITMQ_UNADDRESSED_REQUEST_QUEUE = os.getenv('RABBITMQ_UNADDRESSED_REQUEST_QUEUE', 'unaddressedRequestQueue')
    RABBITMQ_OUTBOUND_FIELD_QUEUE = os.getenv('RABBITMQ_OUTBOUND_FIELD_QUEUE', 'RM.Field')
    RABBITMQ_INBOUND_EQ_QUEUE = os.getenv('RABBITMQ_INBOUND_EQ_QUEUE', 'Case.Responses')
    RABBITMQ_EVENT_EXCHANGE = os.getenv('RABBITMQ_EVENT_EXCHANGE', 'events')
    RABBITMQ_QUESTIONNAIRE_LINKED_ROUTING_KEY = os.getenv('RABBITMQ_QUESTIONNAIRE_LINKED_ROUTING_KEY',
                                                          'event.questionnaire.update')
    RABBITMQ_SAMPLE_TO_ACTION_QUEUE = 'case.action'
    RABBITMQ_REFUSAL_ROUTING_KEY = os.getenv('RABBITMQ_REFUSAL_ROUTING_KEY', 'event.respondent.refusal')
    RABBITMQ_SURVEY_LAUNCHED_ROUTING_KEY = os.getenv('RABBITMQ_SURVEY_LAUNCHED_ROUTING_KEY',
                                                     'event.response.authentication')
    RABBITMQ_FULFILMENT_REQUESTED_ROUTING_KEY = os.getenv('RABBITMQ_FULFILMENT_REQUESTED_ROUTING_KEY',
                                                          'event.fulfilment.request')
    RABBITMQ_ADDRESS_ROUTING_KEY = os.getenv('RABBITMQ_ADDRESS_ROUTING_KEY',
                                             'event.case.address.update')
    RABBITMQ_CCS_PROPERTY_LISTING_ROUTING_KEY = os.getenv('RABBITMQ_CCS_PROPERTY_LISTING_ROUTING_KEY',
                                                          'event.ccs.propertylisting')
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
    OFFLINE_RECEIPT_TOPIC_ID = os.getenv('OFFLINE_RECEIPT_TOPIC_ID', 'offline-receipt-topic')
    PPO_UNDELIVERED_PROJECT_ID = os.getenv("PPO_UNDELIVERED_PROJECT_ID",
                                           "ppo-undelivered-project")
    QM_UNDELIVERED_PROJECT_ID = os.getenv("QM_UNDELIVERED_PROJECT_ID",
                                          "qm-undelivered-project")
    PPO_UNDELIVERED_TOPIC_NAME = "ppo-undelivered-topic"
    QM_UNDELIVERED_TOPIC_NAME = "qm-undelivered-topic"

    GOOGLE_APPLICATION_CREDENTIALS = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    GOOGLE_SERVICE_ACCOUNT_JSON = os.getenv('GOOGLE_SERVICE_ACCOUNT_JSON')

    RABBITMQ_INBOUND_REFUSAL_QUEUE = 'case.refusals'
    RABBITMQ_INBOUND_FULFILMENT_REQUEST_QUEUE = 'case.fulfilments'
    RABBITMQ_INBOUND_NOTIFY_FULFILMENT_REQUEST_QUEUE = 'notify.fulfilments'
    RABBITMQ_OUTBOUND_ADAPTER_EXCHANGE = os.getenv('RABBITMQ_OUTBOUND_ADAPTER_EXCHANGE', 'adapter-outbound-exchange')

    NOTIFY_STUB_HOST = os.getenv('NOTIFY_STUB_HOST', 'localhost')
    NOTIFY_STUB_PORT = os.getenv('NOTIFY_STUB_PORT', '8917')
    NOTIFY_STUB_SERVICE = f'{PROTOCOL}://{NOTIFY_STUB_HOST}:{NOTIFY_STUB_PORT}'

    EXCEPTIONMANAGER_CONNECTION_HOST = os.getenv('EXCEPTIONMANAGER_CONNECTION_HOST', 'localhost')
    EXCEPTIONMANAGER_CONNECTION_PORT = os.getenv('EXCEPTIONMANAGER_CONNECTION_PORT', '8666')
    EXCEPTION_MANAGER_URL = f'http://{EXCEPTIONMANAGER_CONNECTION_HOST}:{EXCEPTIONMANAGER_CONNECTION_PORT}'

    RABBITMQ_QUEUES = ['Action.Field',
                       'Action.Printer',
                       'Case.Responses',
                       'FieldworkAdapter.caseUpdated',
                       'action.events',
                       'action.fulfilment',
                       'case.action',
                       'case.addressQueue',
                       'case.ccsPropertyListedQueue',
                       'case.fulfilments',
                       'case.questionnairelinked',
                       'case.refusals',
                       'case.sample.inbound',
                       'case.uac-qid-created',
                       'case.undeliveredMailQueue',
                       'notify.enriched.fulfilment',
                       'notify.fulfilments',
                       'survey.launched',
                       'unaddressedRequestQueue']

    SENT_PRINT_FILE_BUCKET = os.getenv('SENT_PRINT_FILE_BUCKET', '')

    DB_USERNAME = os.getenv('DB_USERNAME', 'postgres')
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'postgres')
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = os.getenv('DB_PORT', '6432')
    DB_NAME = os.getenv('DB_NAME', 'postgres')
    DB_USESSL = os.getenv('DB_USESSL', '')

    CENSUS_ACTION_PLAN_ID = os.getenv('ACTION_PLAN_ID', 'c4415287-0e37-447b-9c3d-1a011c9fa3db')
    CENSUS_COLLECTION_EXERCISE_ID = os.getenv('COLLECTION_EXERCISE_ID', '34d7f3bb-91c9-45d0-bb2d-90afce4fc790')
