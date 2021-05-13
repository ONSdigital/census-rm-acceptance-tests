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
    CASE_API_CASE_URL = f'{CASEAPI_SERVICE}/cases/'

    ROPS_HOST = os.getenv('ROPS_HOST', 'localhost')
    ROPS_PORT = os.getenv('ROPS_PORT', '8234')

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
    RABBITMQ_FIELD_CASE_UPDATED_ROUTING_KEY = os.getenv('RABBITMQ_FIELD_CASE_UPDATED_ROUTING_KEY',
                                                        'event.fieldcase.update')

    RABBITMQ_DEACTIVATE_UAC_QUEUE = os.getenv('RABBITMQ_DEACTIVATE_UAC_QUEUE', 'case.deactivate-uac')

    RABBITMQ_UNINVALIDATE_ADDRESS_QUEUE = os.getenv('RABBITMQ_UNINVALIDATE_ADDRESS_QUEUE',
                                                    'case.rm.unInvalidateAddress')
    RABBITMQ_NONCOMPLIANCE_QUEUE = os.getenv('RABBITMQ_NONCOMPLIANCE_QUEUE', 'case.rm.nonCompliance')

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
    FULFILMENT_CONFIRMED_PROJECT_ID = os.getenv("FULFILMENT_CONFIRMED_PROJECT_ID",
                                                "fulfilment-confirmed-project")
    FULFILMENT_CONFIRMED_TOPIC_ID = os.getenv("FULFILMENT_CONFIRMED_TOPIC",
                                              "fulfilment-confirmed-topic")
    EQ_FULFILMENT_PROJECT_ID = os.getenv("EQ_FULFILMENT_PROJECT_ID", "eq-fulfilment-project")
    EQ_FULFILMENT_TOPIC_NAME = os.getenv("EQ_FULFILMENT_TOPIC_NAME", "eq-fulfilment-topic")

    AIMS_NEW_ADDRESS_PROJECT = os.getenv("AIMS_NEW_ADDRESS_PROJECT", "aims-new-address-project")
    AIMS_NEW_ADDRESS_TOPIC_NAME = os.getenv("AIMS_NEW_ADDRESS_TOPIC_NAME", "aims-new-address-topic")
    AIMS_NEW_ADDRESS_SUBSCRIPTION = os.getenv("AIMS_NEW_ADDRESS_SUBSCRIPTION", "aims-new-address-subscription")

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

    RABBITMQ_QUEUES_WITH_DLQS = ['Action.Field',
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
    DB_HOST_ACTION = os.getenv('DB_HOST_ACTION', 'localhost')
    DB_HOST_CASE = os.getenv('DB_HOST', 'localhost')
    DB_PORT = os.getenv('DB_PORT', '6432')
    DB_NAME = os.getenv('DB_NAME', 'postgres')
    DB_ACTION_CERTIFICATES = os.getenv('DB_ACTION_CERTIFICATES', '')
    DB_CASE_CERTIFICATES = os.getenv('DB_CASE_CERTIFICATES', '')

    CENSUS_ACTION_PLAN_ID = os.getenv('ACTION_PLAN_ID', 'c4415287-0e37-447b-9c3d-1a011c9fa3db')
    CENSUS_COLLECTION_EXERCISE_ID = os.getenv('COLLECTION_EXERCISE_ID', '34d7f3bb-91c9-45d0-bb2d-90afce4fc790')

    BULK_REFUSAL_BUCKET_NAME = os.getenv('BULK_REFUSAL_BUCKET_NAME')
    BULK_NEW_ADDRESS_BUCKET_NAME = os.getenv('BULK_NEW_ADDRESS_BUCKET_NAME')
    BULK_INVALID_ADDRESS_BUCKET_NAME = os.getenv('BULK_INVALID_ADDRESS_BUCKET_NAME')
    BULK_DEACTIVATE_UAC_BUCKET_NAME = os.getenv('BULK_DEACTIVATE_UAC_BUCKET_NAME')

    BULK_ADDRESS_UPDATE_FILE_PREFIX = os.getenv('BULK_ADDRESS_UPDATE_FILE_PREFIX', 'address_updates_')
    BULK_ADDRESS_UPDATE_BUCKET_NAME = os.getenv('BULK_ADDRESS_UPDATE_BUCKET_NAME')
    BULK_ADDRESS_UPDATE_PROJECT_ID = os.getenv('BULK_ADDRESS_UPDATE_PROJECT_ID')
    BULK_ADDRESS_UPDATE_ROUTING_KEY = os.getenv('BULK_ADDRESS_UPDATE_ROUTING_KEY', 'case.rm.updated')

    BULK_UNINVALIDATED_ADDRESS_FILE_PREFIX = os.getenv('BULK_UNINVALIDATED_ADDRESS_UPDATE_FILE_PREFIX',
                                                       'uninvalidated_addresses_')
    BULK_UNINVALIDATED_ADDRESS_BUCKET_NAME = os.getenv('BULK_UNINVALIDATED_ADDRESS_BUCKET_NAME')
    BULK_UNINVALIDATED_ADDRESS_PROJECT_ID = os.getenv('BULK_UNINVALIDATED_ADDRESS_PROJECT_ID')
    UNINVALIDATED_ADDRESS_EVENT_ROUTING_KEY = os.getenv('BULK_UNINVALIDATED_ADDRESS_ROUTING_KEY',
                                                        'case.rm.unInvalidateAddress')

    BULK_NON_COMPLIANCE_FILE_PREFIX = os.getenv('BULK_NON_COMPLIANCE_FILE_PREFIX', 'non_compliance_')
    BULK_NON_COMPLIANCE_BUCKET_NAME = os.getenv('BULK_NON_COMPLIANCE_BUCKET_NAME')
    BULK_NON_COMPLIANCE_PROJECT_ID = os.getenv('BULK_NON_COMPLIANCE_PROJECT_ID')
    BULK_NON_COMPLIANCE_ROUTING_KEY = os.getenv('BULK_NON_COMPLIANCE_ROUTING_KEY', 'case.rm.nonCompliance')

    BULK_QID_LINK_FILE_PREFIX = os.getenv('BULK_QID_LINK_FILE_PREFIX', 'link_qid_')
    BULK_QID_LINK_BUCKET_NAME = os.getenv('BULK_QID_LINK_BUCKET_NAME')
    BULK_QID_LINK_PROJECT_ID = os.getenv('BULK_QID_LINK_PROJECT_ID')
    BULK_QID_LINK_ROUTING_KEY = os.getenv('BULK_QID_LINK_ROUTING_KEY', 'event.questionnaire.update')

    TREATMENT_CODES = {
        'HH_LP1E', 'HH_LP1W', 'HH_LP2E', 'HH_LP2W', 'HH_QP3E', 'HH_QP3W', 'HH_1ALSFN', 'HH_2BLEFN',
        'HH_2CLEFN', 'HH_3DQSFN', 'HH_3EQSFN', 'HH_3FQSFN', 'HH_3GQSFN', 'HH_4HLPCVN', 'HH_SPGLNFN', 'HH_SPGQNFN',
        'CE_LDIEE', 'CE_LDIEW', 'CE_LDIUE', 'CE_LDIUW', 'CE_QDIEE', 'CE_QDIEW', 'CE_LDCEE', 'CE_LDCEW',
        'CE_1QNFN', 'CE_2LNFN', 'CE_3LSNFN', 'SPG_LPHUE', 'SPG_LPHUW', 'SPG_QDHUE', 'SPG_QDHUW', 'SPG_VDNEE',
        'SPG_VDNEW'}

    ESTAB_TYPES = {'HALL OF RESIDENCE', 'CARE HOME', 'HOSPITAL', 'HOSPICE', 'MENTAL HEALTH HOSPITAL',
                   'MEDICAL CARE OTHER', 'BOARDING SCHOOL', 'LOW/MEDIUM SECURE MENTAL HEALTH',
                   'HIGH SECURE MENTAL HEALTH', 'HOTEL', 'YOUTH HOSTEL', 'HOSTEL', 'MILITARY SLA', 'MILITARY US SLA',
                   'RELIGIOUS COMMUNITY', 'RESIDENTIAL CHILDRENS HOME', 'EDUCATION OTHER', 'PRISON',
                   'IMMIGRATION REMOVAL CENTRE', 'APPROVED PREMISES', 'ROUGH SLEEPER', 'STAFF ACCOMMODATION',
                   'CAMPHILL', 'HOLIDAY PARK', 'HOUSEHOLD', 'SHELTERED ACCOMMODATION', 'RESIDENTIAL CARAVAN',
                   'RESIDENTIAL BOAT', 'GATED APARTMENTS', 'MOD HOUSEHOLDS', 'FOREIGN OFFICES', 'CASTLES', 'GRT SITE',
                   'MILITARY SFA', 'EMBASSY', 'ROYAL HOUSEHOLD', 'CARAVAN', 'MARINA', 'TRAVELLING PERSONS',
                   'TRANSIENT PERSONS', 'MIGRANT WORKERS', 'MILITARY US SFA'}

    CCS_COLLEX_ID = os.getenv('CCS_COLLEX_ID', '6e56db3a-293d-42e6-87b7-556c6c6c92d5')
