Feature: Scheduled initial contact print and manifest files can be generated and uploaded

  Scenario Outline: Generate print files and log events for initial contact letters
    Given sample file "<sample file>" is loaded and correct qids <questionnaire types> set
    When we schedule an action rule of type "<action type>"
    Then correctly formatted "<pack code>" print files are created
    And there is a correct "<pack code>" manifest file for each csv file written
    And events logged against the case are [PRINT_CASE_SELECTED,SAMPLE_LOADED]
    And the files have all been copied to the bucket

    Examples: Initial contact letter: <pack code>
      | pack code     | action type | questionnaire types | sample file                    |
      | D_CE1A_ICLCR1 | CE1_IC01    | [31]                | sample_10_english_CE_estab.csv |

    @smoke
    Examples: Initial contact letter: <pack code>
      | pack code | action type | questionnaire types | sample file                          |
      | P_IC_ICL1 | ICL1E       | [01]                | sample_input_england_census_spec.csv |

    @regression
    Examples: Initial contact letter: <pack code>
      | pack code      | action type | questionnaire types | sample file                        |
      | P_IC_ICL2B     | ICL2W       | [02]                | sample_input_wales_census_spec.csv |
      | P_IC_ICL4      | ICL4N       | [04]                | sample_input_ni_census_spec.csv    |
      | D_CE1A_ICLCR2B | CE1_IC02    | [32]                | sample_for_IC02.csv                |
      | P_ICCE_ICL1    | SPG_IC11    | [01]                | sample_1_english_SPG_unit.csv      |
      | P_ICCE_ICL2B   | SPG_IC12    | [02]                | sample_1_welsh_SPG_unit.csv        |


  Scenario Outline: Generate print files and log events for initial contact letters CE Estabs
    Given sample file "<sample file>" is loaded and correct qids <questionnaire type> set
    When we schedule an action rule of type "<action type>"
    Then CE Estab messages are emitted with <individual qid type> questionnaire types
    And correctly formatted "<pack code>" print files are created for CE Estab expected responses
    And there is a correct "<pack code>" manifest file for each csv file written
    And the expected number of "RM_UAC_CREATED" and [PRINT_CASE_SELECTED,SAMPLE_LOADED] events are logged against the case
    And the files have all been copied to the bucket

    Examples: CE initial contact Letters: <pack code>
      | pack code   | action type | questionnaire type | sample file                   | individual qid type |
      | D_ICA_ICLR1 | CE_IC03     | 31                 | sample_3_english_CE_estab.csv | 21                  |

    @regression
    Examples: CE initial contact Letters: <pack code>
      | pack code    | action type | questionnaire type | sample file                       | individual qid type |
      | D_ICA_ICLR2B | CE_IC04     | 32                 | sample_3_welsh_CE_estab.csv       | 22                  |
      | D_CE4A_ICLR4 | CE_IC05     | 34                 | sample_3_ni_CE_estab_resident.csv | 24                  |
      | D_CE4A_ICLS4 | CE_IC06     | 34                 | sample_3_ni_CE_estab_student.csv  | 24                  |


  Scenario Outline: Generate print files and log events for initial contact questionnaires
    Given sample file "<sample file>" is loaded and correct qids <questionnaire types> set
    When we schedule an action rule of type "<action type>"
    Then correctly formatted "<pack code>" print files are created for questionnaire
    And there is a correct "<pack code>" manifest file for each csv file written
    And events logged against the case are [PRINT_CASE_SELECTED,SAMPLE_LOADED]

    Examples: Initial contact questionnaire: <pack code>
      | pack code | action type | questionnaire types | sample file                                        |
      | P_IC_H1   | ICHHQE      | [01]                | sample_input_census_spec_england_questionnaire.csv |
      | P_IC_H2   | ICHHQW      | [02,03]             | sample_input_census_spec_wales_questionnaire.csv   |

    @regression
    Examples: Initial contact questionnaire: <pack code>
      | pack code | action type | questionnaire types | sample file                                   |
      | P_IC_H4   | ICHHQN      | [04]                | sample_input_census_spec_ni_questionnaire.csv |
      | D_FDCE_H1 | SPG_IC13    | [01]                | sample_3_english_SPG_unit_questionnaire.csv   |
      | D_FDCE_H2 | SPG_IC14    | [02,03]             | sample_3_welsh_SPG_unit_questionnaire.csv     |


  Scenario Outline: Generate print files and log events for CE initial contact questionnaires
    Given sample file "<sample file>" is loaded and correct qids <questionnaire types> set
    When we schedule an action rule of type "<action type>"
    Then CE Estab messages are emitted with <individual qid type> questionnaire types
    And correctly formatted "<pack code>" print files are created for CE Estab questionnaires
    And there is a correct "<pack code>" manifest file for each csv file written
    And the expected number of "RM_UAC_CREATED" and [PRINT_CASE_SELECTED,SAMPLE_LOADED] events are logged against the case

    Examples: CE Estab Initial contact questionnaire: <pack code>
      | pack code | action type | questionnaire types | sample file                          | individual qid type |
      | D_FDCE_I4 | CE_IC08     | [34]                | sample_10_ni_CE_estab_for_sorting.csv | 24                  |

    @regression
    Examples: CE Estab Initial contact questionnaire: <pack code>
      | pack code | action type | questionnaire types | sample file                                 | individual qid type |
      | D_FDCE_I1 | CE_IC09     | [31]                | sample_10_english_CE_estab_for_sorting.csv | 21                  |


  Scenario: Generate print files and log events for Welsh CE initial contact questionnaires
    Given sample file "sample_3_welsh_CE_estab_questionnaire.csv" is loaded and correct qids [32] set
    When we schedule an action rule of type "CE_IC10"
    Then CE Estab messages are emitted with [22,23] questionnaire types
    And correctly formatted "D_FDCE_I2" print files are created for CE Estab Welsh questionnaires
    And there is a correct "D_FDCE_I2" manifest file for each csv file written
    And two "RM_UAC_CREATED" events [PRINT_CASE_SELECTED,SAMPLE_LOADED] are logged per case


  Scenario Outline: Address frame delta initial contact print files
    Given sample file "sample_for_print_stories.csv" is loaded successfully
    And 1 second later delta sample file "<sample file>" is loaded successfully
    When the address frame delta initial contact action rule of type "<action type>" is set
    Then correctly formatted "<pack code>" print files are created
    And there is a correct "<pack code>" manifest file for each csv file written
    And events logged against the case are [PRINT_CASE_SELECTED,SAMPLE_LOADED]
    And the files have all been copied to the bucket

    Examples: Initial contact letter: <pack code>
      | pack code | action type | sample file                          |
      | P_IC_ICL1 | ICL1E       | sample_input_england_census_spec.csv |

    @regression
    Examples: Initial contact letter: <pack code>
      | pack code  | action type | sample file                        |
      | P_IC_ICL2B | ICL2W       | sample_input_wales_census_spec.csv |
      | P_IC_ICL4  | ICL4N       | sample_input_ni_census_spec.csv    |
