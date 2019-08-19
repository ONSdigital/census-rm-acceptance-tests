Feature: Handle refusal message

  Scenario: Refusal message results in case excluded from action plan
    Given an action rule of type ICL1E is set 10 seconds in the future
    And sample file "sample_for_refusals.csv" is loaded
    And messages are emitted to RH and Action Scheduler with [01] questionnaire types
    When a refusal message for a created case is received
    Then only unrefused cases appear in "P_IC_ICL1" print files
    And the case is marked as refused
    And an action instruction cancel message is emitted to FWMT
