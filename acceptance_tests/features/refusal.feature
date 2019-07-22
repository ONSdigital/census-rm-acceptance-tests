Feature: Handle refusal message

  Scenario: Refusal message results case excluded from action plan
    Given an action rule of type FF2QE is set 10 seconds in the future
    When sample file "sample_for_refusals.csv" is loaded
    Then a refusal message for a created case is received
    And the case is marked as refused
    And the case is excluded from FWMT action rule