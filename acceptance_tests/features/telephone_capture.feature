Feature: Telephone capture
  As a respondent
  I want to be able to complete my response over the phone
  So that I can respond in the way I choose

  Scenario Outline: Generate and link correct QID type for unit level cases
    Given sample file "<sample file>" is loaded successfully
    When there is a request for telephone capture for a unit case with case type "<case type>" and country "<country>"
    Then a UAC and QID with questionnaire type "<questionnaire type>" type are generated and returned
    And a UAC updated event is emitted linking the new UAC and QID to the requested case

    Examples:
      | sample file                  | case type | country | questionnaire type |
      | sample_1_english_unit.csv    | HH        | E       | 01                 |
      | sample_1_welsh_unit.csv      | HH        | W       | 02                 |
      | sample_1_ni_unit.csv         | HH        | N       | 04                 |
      | sample_1_english_CE_unit.csv | CE        | E       | 21                 |
      | sample_1_welsh_CE_unit.csv   | CE        | W       | 22                 |
      | sample_1_ni_CE_unit.csv      | CE        | N       | 24                 |
