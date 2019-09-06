Feature: Reminder messages are emitted to Field Work Management Tool

  Scenario: Tranche 2 household case details to be sent to the Field Work Management Tool
    Given an action rule of type "FIELD" is set 10 seconds in the future
    And sample file "sample_for_print_stories.csv" is loaded
    Then the action instruction messages are emitted to FWMT where the case has a treatment code of "HH_QF2R1E"

  Scenario: Check cases sent to Fieldwork are logged in events
    Given an action rule of type "FIELD" is set 2 seconds in the future
    When sample file "sample_for_field.csv" is loaded
    Then messages are emitted to RH and Action Scheduler with 01 questionnaire types
    And events logged against the case are [FIELD_CASE_SELECTED,SAMPLE_LOADED]
