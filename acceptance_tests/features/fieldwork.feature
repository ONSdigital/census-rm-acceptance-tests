Feature: Send messages to fieldwork management tool to keep it in sync with RM

  Scenario: Tranche 2 household case details to be sent to the Field Work Management Tool
    Given an action rule of type FF2QE is set 15 seconds in the future
    And sample file "sample_for_print_stories.csv" is loaded
    Then the action instruction messages are emitted to FWMT where the case has a treatment code of "HH_QF2R1E"