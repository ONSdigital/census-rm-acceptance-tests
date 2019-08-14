Feature: Handle fulfilment request events

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
