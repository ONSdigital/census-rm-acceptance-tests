Feature: A UAC/QID pair can be requested for a case

  Scenario Outline: A UAC/QID pair is requested from case API and the case is subsequently updated with the new pair
    Given sample file "sample_1_english_HH_unit.csv" is loaded successfully
    When a UAC/QID pair is requested with questionnaire type "<questionnaire type>"
    Then a UAC updated message with "<questionnaire type>" questionnaire type is emitted

    @smoke
    Examples: Questionnaire type: <questionnaire type>
      | questionnaire type |
      | 01                 |

    @regression
    Examples: Questionnaire type: <questionnaire type>
      | questionnaire type |
      | 02                 |
      | 04                 |
      | 34                 |
      | 83                 |