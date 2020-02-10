Feature: Handle refusal message

  Scenario: Refusal message results in case excluded from action plan
    Given sample file "sample_for_refusals.csv" is loaded successfully
    And set action rule of type "ICL1E" when the case loading queues are drained
    When a refusal message for a created case is received
    Then only unrefused cases appear in "P_IC_ICL1" print files
    And the case is marked as refused
    And an action instruction cancel message is emitted to FWMT
    And the events logged for the refusal case are [SAMPLE_LOADED,REFUSAL_RECEIVED]