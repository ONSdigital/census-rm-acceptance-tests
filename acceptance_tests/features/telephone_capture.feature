Feature: Telephone capture
  As a respondent
  I want to be able to complete my response over the phone
  So that I can respond in the way I choose

  Scenario: Generate and link correct QID type for an English household case
    Given sample file "sample_1_english_unit.csv" is loaded successfully
    When there is a request for telephone capture for a unit "english" respondent with case type "HH"
    Then a UAC and QID with questionnaire type "01" type are generated and returned
    And a UAC updated event is emitted linking the new UAC and QID to the requested case

  Scenario: Generate and link correct QID type for a unit English CE case
    Given sample file "sample_1_english_CE_unit.csv" is loaded successfully
    When there is a request for telephone capture for a unit "english" respondent with case type "CE"
    Then a UAC and QID with questionnaire type "21" type are generated and returned
    And a UAC updated event is emitted linking the new UAC and QID to the requested case
