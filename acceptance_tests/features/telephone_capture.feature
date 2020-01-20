Feature: Telephone capture
  As a respondent
  I want to be able to complete my response over the phone
  So that I can respond in the way I choose

  Scenario Outline: Generate and link correct QID type for unit level cases
    Given sample file "<sample file>" is loaded successfully
    When there is a request for telephone capture for an address level "<address level>" case with case type "<case type>" and country "<country code>"
    Then a UAC and QID with questionnaire type "<questionnaire type>" type are generated and returned
    And a UAC updated event is emitted linking the new UAC and QID to the requested case

    Examples:
      | sample file                    | address level | case type | country code | questionnaire type |
      | sample_1_englis_HH_unit.csv    | U             | HH        | E            | 01                 |
      | sample_1_welsh_HH_unit.csv     | U             | HH        | W            | 02                 |
      | sample_1_ni_HH_unit.csv        | U             | HH        | N            | 04                 |
      | sample_1_english_CE_unit.csv   | U             | CE        | E            | 21                 |
      | sample_1_welsh_CE_unit.csv     | U             | CE        | W            | 22                 |
      | sample_1_ni_CE_unit.csv        | U             | CE        | N            | 24                 |
      | sample_1_english_SPG_unit.csv  | U             | SPG       | E            | 01                 |
      | sample_1_welsh_SPG_unit.csv    | U             | SPG       | W            | 02                 |
      | sample_1_english_SPG_estab.csv | E             | SPG       | E            | 01                 |
      | sample_1_welsh_SPG_estab.csv   | E             | SPG       | W            | 02                 |

  Scenario Outline: Individual telephone capture request creates new individual case and correct type QID UAC pair and links them
    Given sample file "<sample file>" is loaded successfully
    When there is a request for individual telephone capture for a unit case with case type "<case type>" and country "<country code>"
    Then a UAC and QID with questionnaire type "<questionnaire type>" type are generated and returned
    And a new individual child case for telephone capture is emitted to RH and Action Scheduler
    And a UAC updated event is emitted linking the new UAC and QID to the individual case

    Examples:
      | sample file                 | case type | country code | questionnaire type |
      | sample_1_englis_HH_unit.csv | HH        | E            | 21                 |
      | sample_1_welsh_HH_unit.csv  | HH        | W            | 22                 |
      | sample_1_ni_HH_unit.csv     | HH        | N            | 24                 |
