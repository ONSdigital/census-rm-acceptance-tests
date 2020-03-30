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


  Scenario: Log Address Modified Event
    Given sample file "sample_1_english_HH_unit.csv" is loaded successfully
    When an Address Modified Event is sent
    Then events logged against the case are [SAMPLE_LOADED,ADDRESS_MODIFIED]


  Scenario: Log AddressTypeChanged event
    Given sample file "sample_1_english_HH_unit.csv" is loaded successfully
    When an AddressTypeChanged event is sent
    And events logged against the case are [SAMPLE_LOADED,ADDRESS_TYPE_CHANGED]


