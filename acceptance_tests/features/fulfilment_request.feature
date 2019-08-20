Feature: Handle fulfilment request events

  Scenario: Log event when a fulfilment request event is received
    Given sample file "sample_input_england_census_spec.csv" is loaded
    And messages are emitted to RH and Action Scheduler with [01] questionnaire types
    When a UAC fulfilment request "UACHHT1" message for a created case is sent
    Then a fulfilment request event is logged
    And notify api was called

  Scenario: Individual Response Fulfilment is received Log event without contact details, save new case, emit new case
    Given sample file "sample_input_england_census_spec.csv" is loaded
    And messages are emitted to RH and Action Scheduler with [01] questionnaire types
    When a UAC fulfilment request "UACIT1" message for a created case is sent
    Then a fulfilment request event is logged
    And a new child case is emitted to RH and Action Scheduler
    And notify api was called

  Scenario Outline: Generate print file and log an event when an England fulfilment request event is received
    Given sample file "sample_1_english_unit.csv" is loaded
    And messages are emitted to RH and Action Scheduler with [01] questionnaire types
    When a PQ fulfilment request event with fulfilment code "<fulfilment code>" is received by RM
    Then a UAC updated message with "<questionnaire type>" questionnaire type is emitted
    And correctly formatted on request questionnaire print and manifest files for "<fulfilment code>" are created
    And the fulfilment request event is logged

    Examples: Fulfilment codes
      | fulfilment code | questionnaire type |
      | P_OR_H1         | 01                 |
      | P_OR_H2         | 02                 |
      | P_OR_H2W        | 03                 |
      | P_OR_H4         | 04                 |
