Feature: Handle fulfilment request events

  Scenario: Generate print file and log an event when an England fulfilment request event is received
    Given sample file "sample_input_england_census_spec.csv" is loaded
    And messages are emitted to RH and Action Scheduler with [01] questionnaire types
    When a PQ fulfilment request event with fulfilment code "P_OR_H1" is received by RM
    Then an ad hoc UAC updated message with "01" questionnaire type is emitted
    And correctly formatted "P_OR_H1" on request questionnaire print files are created
    And the fulfilment request event is logged
