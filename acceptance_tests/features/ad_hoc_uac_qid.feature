Feature: A UAC/QID pair can be requested for a case

  Scenario Outline: A UAC/QID pair is requested from case API and the case is subsequently updated with the new pair
    Given sample file "sample_for_fulfilment_requests.csv" is loaded
    And messages are emitted to RH and Action Scheduler with [01] questionnaire types
    When a UAC/QID pair is requested with questionnaire type "<questionnaire type>"
    Then a UAC updated message with "<questionnaire type>" questionnaire type is emitted

    Examples: Questionnaire types
      | questionnaire type |
      | 01                 |
      | 02                 |
      | 04                 |
      | 37                 |
      | 99                 |