Feature: Handle fulfilment request events

  Scenario: Log event when a fulfilment request event is received
    Given sample file "sample_input_england_census_spec.csv" is loaded
    And messages are emitted to RH and Action Scheduler with [01] qids
    When a fulfilment request message for a created case is sent
    Then a fulfilment request event is logged


  Scenario: UAC fulfilment request event logged and sent to notify service
    Given sample file "sample_input_england_census_spec.csv" is loaded
    And messages are emitted to RH and Action Scheduler with [01] qids
    When a UAC fulfilment request message for a created case is sent
    Then a fulfilment request event is logged
    And notify api was called