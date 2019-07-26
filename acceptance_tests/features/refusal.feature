Feature: Handle refusal message

  Scenario: Refusal message results case excluded from action plan
    Given an action rule of type ICL1E is set 10 seconds in the future
    When sample file "sample_for_refusals.csv" is loaded
    Then messages are emitted to RH and Action Scheduler with [01] qids
    And a refusal message for a created case is received
    And the case is marked as refused
    And only unrefused cases appear in "P_IC_ICL1" print files
