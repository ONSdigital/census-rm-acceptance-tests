Feature: Reminder messages are emitted to Field Work Management Tool

  Scenario: Tranche 2 household case details to be sent to the Field Work Management Tool
    Given sample file "sample_for_print_stories.csv" is loaded successfully
    And an action rule of type "FIELD" is set 5 seconds in the future
    When the action instruction messages are emitted to FWMT where the case has a "treatmentCode" of "HH_QF2R1E"
    Then the events logged against the tranche 2 fieldwork cases are [FIELD_CASE_SELECTED,SAMPLE_LOADED]


  Scenario: send community estab cases to field
    Given sample file "sample_for_ce_stories.csv" is loaded successfully
    When an action rule for address type "CE" is set 5 seconds in the future
    Then the action instruction is emitted to FWMT where case has a "caseType" of "CE" and CEComplete is "false"

  Scenario: send SPG cases to field
    Given sample file "sample_for_spg_stories.csv" is loaded successfully
    When an action rule for address type "SPG" is set 5 seconds in the future
    Then the action instruction is emitted to FWMT where case has a "caseType" of "SPG" and CEComplete is "false"
