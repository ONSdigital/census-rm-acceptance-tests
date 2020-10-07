Feature: Address updates

  Scenario Outline: Invalid address event for HH, CE and SPG address types for unit level cases
    Given sample file "<sample file>" is loaded successfully
    When an invalid address message is sent from "CC"
    Then a case_updated msg is emitted where "addressInvalid" is "True"
    And a CANCEL action instruction is sent to field work management with address type "<address type>"
    And the case event log records invalid address

    Examples:
      | sample file                          | address type |
      | sample_for_questionnaire_linked.csv  | HH           |
      | sample_for_invalid_address_CE_U.csv  | CE           |
      | sample_for_invalid_address_SPG_U.csv | SPG          |


  Scenario Outline: Invalid address event for CE and SPG address types for Estab level cases
    Given sample file "<sample file>" is loaded successfully
    When an invalid address message is sent from "CC"
    Then a case_updated msg is emitted where "addressInvalid" is "True"
    And a CANCEL action instruction is sent to field work management with address type "<address type>"
    And the case event log records invalid address

    Examples:
      | sample file                          | address type |
      | sample_for_invalid_address_CE_E.csv  | CE           |
      | sample_for_invalid_address_SPG_E.csv | SPG          |


  Scenario: Invalid address event for CCS unit level case
    Given a CCS Property List event is sent and associated "HH" case is created and sent to FWMT
    When an invalid address message for the CCS case is sent from "CC"
    Then a case_updated msg is emitted where "addressInvalid" is "True"
    And a CANCEL action instruction is sent to field work management with address type "HH"
    And the case event log records invalid address


  Scenario: New address event received without sourceCaseId with UPRN
    When a NEW_ADDRESS_REPORTED event is sent from "FIELD" without sourceCaseId with UPRN
    Then a case created event is emitted
    And the case with UPRN from the New Address event can be retrieved
    And the events logged for the case are [NEW_ADDRESS_REPORTED]


  Scenario: New address event received for CE case without sourceCaseId and Secure Establishment True
    When a NEW_ADDRESS_REPORTED event for a CE case is sent from "FIELD" without a sourceCaseId
    Then a case created event is emitted
    And the CE case with secureEstablishment marked True from the New Address event can be retrieved
    And the events logged for the case are [NEW_ADDRESS_REPORTED]


  Scenario: New address event received for CE case without sourceCaseId and no secureType recorded
    When a NEW_ADDRESS_REPORTED event for a CE case is sent from "FIELD" without a sourceCaseId and no secureType
    Then a case created event is emitted
    And the CE case with secureEstablishment marked False from the New Address event can be retrieved
    And the events logged for the case are [NEW_ADDRESS_REPORTED]


  Scenario: New address event received for CE case with sourceCaseId and Secure Establishment True
    Given sample file "sample_1_english_CE_secure_estab.csv" is loaded successfully
    When a NEW_ADDRESS_REPORTED event for a CE case is sent from "FIELD" with sourceCaseId and secureType true
    Then a case created event is emitted
    And the CE case can be retrieved and contains the correct properties when the event had details
    And the events logged for the case are [NEW_ADDRESS_REPORTED]
    And the new address reported cases are sent to field as CREATE with secureEstablishment as true


  Scenario: New address event received for CE case with sourceCaseId and Secure Establishment False
    Given sample file "sample_1_english_CE_secure_estab.csv" is loaded successfully
    When a NEW_ADDRESS_REPORTED event for a CE case is sent from "FIELD" with sourceCaseId and secureType false
    Then a case created event is emitted
    And the CE case can be retrieved and contains the correct properties when the event had details
    And the events logged for the case are [NEW_ADDRESS_REPORTED]
    And the new address reported cases are sent to field as CREATE with secureEstablishment as false


  Scenario: New address event received with sourceCaseId
    Given sample file "sample_1_english_HH_unit.csv" is loaded successfully
    When a NEW_ADDRESS_REPORTED event is sent from "FIELD" with sourceCaseId
    Then a case created event is emitted
    And the case can be retrieved and contains the correct properties when the event had details
    And the events logged for the case are [NEW_ADDRESS_REPORTED]


  Scenario: New address event received with sourceCaseId and minimal event fields
    Given sample file "sample_1_english_HH_unit.csv" is loaded successfully
    When a NEW_ADDRESS_REPORTED event is sent from "FIELD" with sourceCaseId and minimal event fields
    Then a case created event is emitted
    And the case can be retrieved and contains the correct properties when the event had minimal details
    And the events logged for the case are [NEW_ADDRESS_REPORTED]


  Scenario: Modified address event received
    Given sample file "sample_1_english_CE_estab.csv" is loaded successfully
    When an Address Modified Event is sent
    Then a case updated msg is emitted with the updated case details
    And events logged against the case are [SAMPLE_LOADED,ADDRESS_MODIFIED]


  Scenario Outline: AddressTypeChanged event
    Given sample file "<sample file>" is loaded successfully
    When an AddressTypeChanged event to "<target address type>" is sent
    Then a case_updated msg is emitted where "addressInvalid" is "True"
    And events logged against the case are [SAMPLE_LOADED,ADDRESS_NOT_VALID,ADDRESS_TYPE_CHANGED]
    And a case created event is emitted
    And the "<target address type>" case with level "<derived address level>" has the correct values
    And events logged against the case are [ADDRESS_TYPE_CHANGED]

    Examples:
      | sample file                  | target address type | derived address level |
      | sample_1_english_HH_unit.csv | CE                  | E                     |

    @regression
    Examples:
      | sample file                    | target address type | derived address level |
      | sample_1_english_HH_unit.csv   | SPG                 | U                     |
      | sample_1_english_CE_estab.csv  | HH                  | U                     |
      | sample_1_english_CE_estab.csv  | SPG                 | U                     |
      | sample_1_english_SPG_estab.csv | HH                  | U                     |
      | sample_1_english_SPG_estab.csv | CE                  | E                     |


  Scenario: Fulfilment request for new skeleton case
    Given a NEW_ADDRESS_REPORTED event is sent from "FIELD" without sourceCaseId and new case is emitted
    When a PQ fulfilment request event with fulfilment code "P_OR_H1" is received by RM
    Then a UAC updated message with "01" questionnaire type is emitted
    And correctly formatted on request questionnaire print and manifest files for "P_OR_H1" are created
    And the questionnaire fulfilment case has these events logged [NEW_ADDRESS_REPORTED,FULFILMENT_REQUESTED,RM_UAC_CREATED,PRINT_CASE_SELECTED]


  @hardcoded_census_values_for_collection_and_action_plan_ids
  Scenario: Individual Telephone capture for new skeleton case
    Given a NEW_ADDRESS_REPORTED event with address type "HH" is sent from "FIELD" and the case is created
    When there is a request for a new HI case for telephone capture for the parent case with address type "HH" and country "E"
    Then a UAC and QID with questionnaire type "21" type are generated and returned
    And a new individual child case for telephone capture is emitted to RH and Action Scheduler
    And a UAC updated event is emitted linking the new UAC and QID to the individual case


  Scenario: New address event received with sourceCaseId and sends Create to Field
    Given sample file "sample_1_english_SPG_estab.csv" is loaded successfully
    When a NEW_ADDRESS_REPORTED event is sent from "FIELD" with sourceCaseId
    And a case created event is emitted
    And a CREATE action instruction is sent to field for the SPG case


# TODO: Re-instate this scenario when we've implemented response-driven reminders for Census 2021
#  @hardcoded_census_values_for_collection_and_action_plan_ids
#  Scenario: Skeleton cases are excluded from action rules
#    Given sample file "sample_1_english_SPG_unit.csv" is loaded successfully
#    And a NEW_ADDRESS_REPORTED event is sent from "FIELD" with sourceCaseId
#    And a case created event is emitted
#    When we schedule an action rule of type "P_RD_2RL1_1" for LSOAs ('E01014540')
#    Then skeleton cases do not appear in "P_RD_2RL1_1" print files


  Scenario Outline: Telephone capture for new skeleton case
    Given a NEW_ADDRESS_REPORTED event is sent from "FIELD" without sourceCaseId with region "<country code>", address type "<address type>" and address level "<address level>" and case emitted
    When there is a request for telephone capture for an address level "<address level>" case with address type "<address type>" and country "<country code>"
    Then a UAC and QID with questionnaire type "<questionnaire type>" type are generated and returned
    And a UAC updated event is emitted linking the new UAC and QID to the requested case
    And a fulfilment request event is logged

    Examples:
      | address level | address type | country code | questionnaire type |
      | U             | HH           | E            | 01                 |
      | U             | SPG          | E            | 01                 |
      | E             | CE           | E            | 31                 |
      | E             | SPG          | E            | 01                 |

    @regression
    Examples:
      | address level | address type | country code | questionnaire type |
      | U             | HH           | W            | 02                 |
      | U             | SPG          | W            | 02                 |
      | E             | CE           | W            | 32                 |
      | E             | SPG          | W            | 02                 |
      | U             | HH           | N            | 04                 |
      | U             | SPG          | N            | 04                 |
      | E             | CE           | N            | 34                 |
      | E             | SPG          | N            | 04                 |


  @hardcoded_census_values_for_collection_and_action_plan_ids
  Scenario Outline: Individual Telephone capture for new skeleton case - CE & SPG cases
    Given a NEW_ADDRESS_REPORTED event with region "<country code>", address type "<address type>" and address level "<address level>" is sent from "FIELD" and case emitted
    When there is a request for individual telephone capture for the case with address type "<address type>" and country "<country code>"
    Then a UAC and QID with questionnaire type "<questionnaire type>" type are generated and returned
    And a UAC updated event is emitted linking the new UAC and QID to the requested case

    Examples:
      | address level | address type | country code | questionnaire type |
      | U             | CE           | E            | 21                 |
      | E             | CE           | E            | 21                 |
      | E             | SPG          | E            | 21                 |
      | U             | SPG          | E            | 21                 |

    @regression
    Examples:
      | address level | address type | country code | questionnaire type |
      | U             | SPG          | W            | 22                 |
      | E             | CE           | W            | 22                 |
      | E             | SPG          | W            | 22                 |
      | U             | SPG          | N            | 24                 |
      | E             | CE           | N            | 24                 |
      | E             | SPG          | N            | 24                 |

  @purge_aims_subscription
  Scenario: New address event received without sourceCaseId and without UPRN
    When a NEW_ADDRESS_REPORTED event is sent from "FIELD" without sourceCaseId or UPRN
    Then a NEW_ADDRESS_ENHANCED event is sent to aims
    And a case created event is emitted
    And the case with dummy UPRN from the New Address event can be retrieved
    And the events logged for the case are [NEW_ADDRESS_REPORTED]
