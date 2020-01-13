Feature: Telephone capture
  As a respondent
  I want to be able to complete my response over the phone
  So that I can respond in the way I choose

  Scenario: Generate correct QID type
    Given sample file "sample_1_english_unit.csv" is loaded successfully
    When there is a request for telephone capture for an english respondent with case type HH
    Then generate and return a UAC and the correct english HH QID type
    And a UAC updated message with "01" questionnaire type is emitted
