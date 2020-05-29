Feature: Handle refusal message

  Scenario Outline: Refusal message results in case excluded from refusal print file
    Given sample file "sample_for_refusals.csv" is loaded successfully
    When a refusal message for the created case is received of type "<refusal type>"
    Then a CANCEL action instruction is emitted to FWMT
    And set action rule of type "<action type>" when case event "REFUSAL_RECEIVED" is logged
    And only unrefused or HARD_REFUSAL cases appear in "P_IC_ICL1" print files of refusal type "<refusal type>"
    And the case is marked as refused
    And the events logged for the refusal case are [SAMPLE_LOADED,REFUSAL_RECEIVED]

    Examples: Refusal types to print file
      | action type | refusal type          |
      | ICL1E       | HARD_REFUSAL          |
      | ICL1E       | EXTRAORDINARY_REFUSAL |


  @smoke
  Scenario: Refusal message results in CCS case excluded from action plan
    Given a CCS Property Listed event is sent
    And the CCS Property Listed case is created with address type "HH"
    And the correct ActionInstruction is sent to FWMT
    When a refusal message for the created CCS case is received
    Then the case is marked as refused
    And a CANCEL action instruction is emitted to FWMT
    And the events logged for the refusal case are [CCS_ADDRESS_LISTED,REFUSAL_RECEIVED]