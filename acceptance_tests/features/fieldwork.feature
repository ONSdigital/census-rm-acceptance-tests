Feature: Send messages to fieldwork management tool to keep it in sync with RM

  Scenario: Tranche 2 household case details to be sent to the Field Work Management Tool
    Given an action rule of type FF2QE is set 10 seconds in the future
    And sample file "sample_input_england_census_spec.csv" is loaded
    Then the action instruction messages are emitted to FWMT