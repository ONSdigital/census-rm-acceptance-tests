Feature: Handle refusal message

  Scenario: Refusal message results in case excluded from action plan
    Given sample file "sample_for_refusals.csv" is loaded successfully
    When a refusal message for the created case is received
    And set action rule of type "ICL1E" when case event "REFUSAL_RECEIVED" is logged
    Then only unrefused cases appear in "P_IC_ICL1" print files
    And the case is marked as refused
    And an action instruction cancel message is emitted to FWMT
    And the events logged for the refusal case are [SAMPLE_LOADED,REFUSAL_RECEIVED]

  Scenario: Refusal message results in CCS case excluded from action plan
    Given a CCS Property Listed event is sent
    And the CCS Property Listed case is created with case_type "HH"
    And the correct ActionInstruction is sent to FWMT
    When a refusal message for the created CCS case is received
    Then the case is marked as refused
    And an action instruction cancel message is emitted to FWMT
    And the events logged for the refusal case are [CCS_ADDRESS_LISTED,REFUSAL_RECEIVED]
