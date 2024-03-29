Feature: Handle refusal message

  Scenario Outline: Refusal message from Contact Centre results in case excluded from refusal print file
    Given sample file "sample_for_refusals_print.csv" is loaded successfully
    When a refusal message of type "<refusal type>" is sent from "CC" for the created case
    Then a CANCEL action instruction is emitted to FWMT for the refused case
    And we schedule an action rule of type "ICL1E" when case event "REFUSAL_RECEIVED" is logged
    And the refused case of type "<refusal type>" only appears in the "P_IC_ICL1" print files if it is a HARD_REFUSAL
    And the case is marked as refused
    And the events logged for the refusal case are <events expected>

    Examples: Refusal types to print file
      | refusal type          | events expected                                      |
      | HARD_REFUSAL          | [SAMPLE_LOADED,REFUSAL_RECEIVED,PRINT_CASE_SELECTED] |
      | EXTRAORDINARY_REFUSAL | [SAMPLE_LOADED,REFUSAL_RECEIVED]                     |


  Scenario Outline: All Contact Centre refusal types result in case excluded from Fieldwork followup
    Given sample file "sample_for_refusals_field.csv" is loaded successfully
    When a refusal message of type "<refusal type>" is sent from "CC" for the created case
    Then a CANCEL action instruction is emitted to FWMT for the refused case
    And we schedule an action rule of type "FIELD" when case event "REFUSAL_RECEIVED" is logged
    And Only unrefused cases are sent to field
    And the case is marked as refused
    And the events logged for the refusal case are [SAMPLE_LOADED,REFUSAL_RECEIVED]

    Examples: Refusal types
      | refusal type          |
      | HARD_REFUSAL          |
      | EXTRAORDINARY_REFUSAL |

  @regression
  Scenario: Refusal message from Field results in case excluded from refusal print file and a cancel message is not sent to field
    Given sample file "sample_for_refusals_field.csv" is loaded successfully
    When a refusal message of type "HARD_REFUSAL" is sent from "FIELD" for the created case
    Then no ActionInstruction is sent to FWMT
    And we schedule an action rule of type "FIELD" when case event "REFUSAL_RECEIVED" is logged
    And Only unrefused cases are sent to field
    And the case is marked as refused
    And the events logged for the refusal case are [SAMPLE_LOADED,REFUSAL_RECEIVED]


  @smoke
  Scenario: Refusal message results in CCS case excluded from action plan
    Given a CCS Property List event is sent and associated "HH" case is created and sent to FWMT
    When a refusal message for the created CCS case is received
    Then the case is marked as refused
    And a CANCEL action instruction is emitted to FWMT for the refused case
    And the events logged for the refusal case are [CCS_ADDRESS_LISTED,REFUSAL_RECEIVED]