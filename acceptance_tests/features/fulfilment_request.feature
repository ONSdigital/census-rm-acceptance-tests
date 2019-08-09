Feature: Handle fulfilment request events

  Scenario: Generate print file and log an event when a fulfilment request event is received
    Given sample file "sample_input_england_census_spec.csv" is loaded
    When a PQ fulfilment request event with fulfilment code "P_OR_H1" is received by RM
    Then correctly formatted "P_OR_H1" on request questionnaire print files are created
    And a fulfilment request event is logged
