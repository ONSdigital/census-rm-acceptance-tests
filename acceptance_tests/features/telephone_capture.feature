Feature: Telephone capture
  As a respondent
  I want to be able to complete my response over the phone
  So that I can respond in the way I choose

  Scenario Outline: Generate and link correct QID type for non individual telephone capture requests
    Given sample file "<sample file>" is loaded successfully
    When there is a request for telephone capture for an address level "<address level>" case with address type "<address type>" and country "<country code>"
    Then a UAC and QID with questionnaire type "<questionnaire type>" type are generated and returned
    And a UAC updated event is emitted linking the new UAC and QID to the requested case
    And a fulfilment request event is logged

    @smoke
    Examples:
      | sample file                    | address level | address type | country code | questionnaire type |
      | sample_1_english_HH_unit.csv   | U             | HH           | E            | 01                 |

    Examples:
      | sample file                    | address level | address type | country code | questionnaire type |
      | sample_1_welsh_HH_unit.csv     | U             | HH           | W            | 02                 |
      | sample_1_ni_HH_unit.csv        | U             | HH           | N            | 04                 |
      | sample_1_english_CE_estab.csv  | E             | CE           | E            | 31                 |
      | sample_1_welsh_CE_estab.csv    | E             | CE           | W            | 32                 |
      | sample_1_ni_CE_estab.csv       | E             | CE           | N            | 34                 |
      | sample_1_english_SPG_unit.csv  | U             | SPG          | E            | 01                 |
      | sample_1_welsh_SPG_unit.csv    | U             | SPG          | W            | 02                 |
      | sample_1_english_SPG_estab.csv | E             | SPG          | E            | 01                 |
      | sample_1_welsh_SPG_estab.csv   | E             | SPG          | W            | 02                 |

  Scenario Outline: Generate and link new HI case and correct QID type for HI individual telephone capture requests
    Given sample file "<sample file>" is loaded successfully
    When there is a request for a new HI case for telephone capture for the parent case with address type "<address type>" and country "<country code>"
    Then a UAC and QID with questionnaire type "<questionnaire type>" type are generated and returned
    And a new individual child case for telephone capture is emitted to RH and Action Scheduler
    And a UAC updated event is emitted linking the new UAC and QID to the individual case

    Examples:
      | sample file                  | address type | country code | questionnaire type |
      | sample_1_english_HH_unit.csv | HH           | E            | 21                 |
      | sample_1_welsh_HH_unit.csv   | HH           | W            | 22                 |
      | sample_1_ni_HH_unit.csv      | HH           | N            | 24                 |


  Scenario Outline: Generate and link correct individual QID type for individual telephone capture requests
    Given sample file "<sample file>" is loaded successfully
    When there is a request for individual telephone capture for the case with address type "<address type>" and country "<country code>"
    Then a UAC and QID with questionnaire type "<questionnaire type>" type are generated and returned
    And a UAC updated event is emitted linking the new UAC and QID to the requested case
    And a fulfilment request event is logged

    Examples:
      | sample file                    | address type | country code | questionnaire type |
      | sample_1_english_SPG_unit.csv  | SPG          | E            | 21                 |
      | sample_1_welsh_SPG_unit.csv    | SPG          | W            | 22                 |
      | sample_1_ni_SPG_unit.csv       | SPG          | N            | 24                 |
      | sample_1_english_SPG_estab.csv | SPG          | E            | 21                 |
      | sample_1_welsh_SPG_estab.csv   | SPG          | W            | 22                 |
      | sample_1_ni_SPG_estab.csv      | SPG          | N            | 24                 |
      | sample_1_english_CE_estab.csv  | CE           | E            | 21                 |
      | sample_1_welsh_CE_estab.csv    | CE           | W            | 22                 |
      | sample_1_ni_CE_estab.csv       | CE           | N            | 24                 |
      | sample_1_english_CE_unit.csv   | CE           | E            | 21                 |
      | sample_1_welsh_CE_unit.csv     | CE           | W            | 22                 |
      | sample_1_ni_CE_unit.csv        | CE           | N            | 24                 |
