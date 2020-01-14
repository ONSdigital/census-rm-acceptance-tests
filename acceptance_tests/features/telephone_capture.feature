Feature: Telephone capture
  As a respondent
  I want to be able to complete my response over the phone
  So that I can respond in the way I choose

  Scenario: Generate correct QID type
    Given sample file "sample_1_english_unit.csv" is loaded successfully
    When there is a request for telephone capture for an english respondent with case type HH
    Then a UAC and QID with questionnaire type "01" type are generated and returned
    And a UAC updated message linking the new UAC and QID to the requested case is emitted
