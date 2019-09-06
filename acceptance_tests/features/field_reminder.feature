Feature: Reminder messages are emitted to Field Work Management Tool

  Scenario: Tranche 2 household case details to be sent to the Field Work Management Tool
    Given sample file "sample_for_print_stories.csv" is loaded successfully
    And an action rule of type "FIELD" is set 5 seconds in the future
    When the action instruction messages are emitted to FWMT where the case has a treatment code of "HH_QF2R1E"
    Then the events logged against the tranche 2 fieldwork cases are [FIELD_CASE_SELECTED,SAMPLE_LOADED]
