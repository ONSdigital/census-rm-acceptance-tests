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
    Given a CCS Property Listed event is sent
    And the CCS Property Listed case is created with address type "HH"
    And the correct ActionInstruction is sent to FWMT
    When an invalid address message for the CCS case is sent from "CC"
    Then a case_updated msg is emitted where "addressInvalid" is "True"
    And a CANCEL action instruction is sent to field work management with address type "HH"
    And the case event log records invalid address


  Scenario: New address event received without sourceCaseId
    Given a NEW_ADDRESS_REPORTED event is sent from "FIELD" without sourceCaseId
    When a case created event is emitted
    Then the case can be retrieved
    And the events logged for the case are [NEW_ADDRESS_REPORTED]


  Scenario: New address event received with sourceCaseId
    Given sample file "sample_1_english_HH_unit.csv" is loaded successfully
    When a NEW_ADDRESS_REPORTED event is sent from "FIELD" with sourceCaseId
    And a case created event is emitted
    Then the case can be retrieved and contains the correct properties when the event had details
    And the events logged for the case are [NEW_ADDRESS_REPORTED]


  Scenario: New address event received with sourceCaseId and minimal event fields
    Given sample file "sample_1_english_HH_unit.csv" is loaded successfully
    When a NEW_ADDRESS_REPORTED event is sent from "FIELD" with sourceCaseId and minimal event fields
    And a case created event is emitted
    Then the case can be retrieved and contains the correct properties when the event had minimal details
    And the events logged for the case are [NEW_ADDRESS_REPORTED]


  Scenario: Log Address Modified Event
    Given sample file "sample_1_english_HH_unit.csv" is loaded successfully
    When an Address Modified Event is sent
    Then events logged against the case are [SAMPLE_LOADED,ADDRESS_MODIFIED]


  Scenario: Log AddressTypeChanged event
    Given sample file "sample_1_english_HH_unit.csv" is loaded successfully
    When an AddressTypeChanged event is sent
    And events logged against the case are [SAMPLE_LOADED,ADDRESS_TYPE_CHANGED]

  Scenario: Fulfilment request for new skeleton case
    Given a NEW_ADDRESS_REPORTED event is sent from "FIELD" without sourceCaseId
    And a case created event is emitted
    When a PQ fulfilment request event with fulfilment code "P_OR_H1" is received by RM
    Then a UAC updated message with "01" questionnaire type is emitted
    And correctly formatted on request questionnaire print and manifest files for "P_OR_H1" are created
    And the questionnaire fulfilment case has these events logged [NEW_ADDRESS_REPORTED,FULFILMENT_REQUESTED,RM_UAC_CREATED,PRINT_CASE_SELECTED]


  Scenario: Individual Telephone capture for new skeleton case
    Given the action plan and collection exercises IDs are the hardcoded census values
    And a NEW_ADDRESS_REPORTED event with address type "HH" is sent from "FIELD"
    And a case created event is emitted
    When there is a request for a new HI case for telephone capture for the parent case with address type "HH" and country "E"
    Then a UAC and QID with questionnaire type "21" type are generated and returned
    And a new individual child case for telephone capture is emitted to RH and Action Scheduler
    And a UAC updated event is emitted linking the new UAC and QID to the individual case

  Scenario: New address event received with sourceCaseId and sends Create to Field
    Given sample file "sample_1_english_SPG_estab.csv" is loaded successfully
    When a NEW_ADDRESS_REPORTED event is sent from "FIELD" with sourceCaseId
    And a case created event is emitted
    And a CREATE action instruction is sent to field

  Scenario: Skeleton cases are excluded from action rules
    Given the action plan and collection exercises IDs are the hardcoded census values
    And sample file "sample_1_english_SPG_unit.csv" is loaded successfully
    And a NEW_ADDRESS_REPORTED event is sent from "FIELD" with sourceCaseId
    And a case created event is emitted
    When set action rule of type "P_RD_2RL1_1"
    Then skeleton cases do not appear in "P_RD_2RL1_1" print files


  Scenario Outline: Telephone capture for new skeleton case
    Given a NEW_ADDRESS_REPORTED event is sent from "FIELD" without sourceCaseId with region "<country code>", address type "<address type>" and address level "<address level>"
    And a case created event is emitted
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

  Scenario Outline: Individual Telephone capture for new skeleton case - CE & SPG cases
    Given the action plan and collection exercises IDs are the hardcoded census values
    And a NEW_ADDRESS_REPORTED event with region "<country code>", address type "<address type>" and address level "<address level>" is sent from "FIELD"
    And a case created event is emitted
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

