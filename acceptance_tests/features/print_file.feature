Feature: Scheduled print and manifest files can be generated and uploaded

  Scenario Outline: Generate print files and log events for initial contact letters
    Given sample file "<sample file>" is loaded
    And messages are emitted to RH and Action Scheduler with <questionnaire types> questionnaire types
    When set action rule of type "<action type>" when the case loading queues are drained
    Then correctly formatted "<pack code>" print files are created
    And there is a correct "<pack code>" manifest file for each csv file written
    And events logged against the case are [PRINT_CASE_SELECTED,SAMPLE_LOADED]
    And the files have all been copied to the bucket

    Examples: Initial contact letter: <pack code>
      | pack code      | action type | questionnaire types | sample file                        |
      | D_CE1A_ICLCR1  | CE1_IC01    | [31]                | sample_10_english_CE_estab.csv     |

    @smoke
    Examples: Initial contact letter: <pack code>
      | pack code | action type | questionnaire types | sample file                          |
      | P_IC_ICL1 | ICL1E       | [01]                | sample_input_england_census_spec.csv |

    @regression
    Examples: Initial contact letter: <pack code>
      | pack code      | action type | questionnaire types | sample file                        |
      | P_IC_ICL2B     | ICL2W       | [02]                | sample_input_wales_census_spec.csv |
      | P_IC_ICL4      | ICL4N       | [04]                | sample_input_ni_census_spec.csv    |
      | D_CE1A_ICLCR2B | CE1_IC02    | [32]                | sample_1_welsh_CE_estab.csv        |
      | D_ICA_ICLR1    | CE_IC03_1   | [21]                | sample_1_english_CE_unit.csv       |
      | D_ICA_ICLR2B   | CE_IC04_1   | [22]                | sample_1_welsh_CE_unit.csv         |
      | P_ICCE_ICL1    | SPG_IC11    | [01]                | sample_1_english_SPG_unit.csv      |
      | P_ICCE_ICL2B   | SPG_IC12    | [02]                | sample_1_welsh_SPG_unit.csv        |


  Scenario Outline: Generate print files and log events for initial contact letters CE Estabs
    Given sample file "<sample file>" is loaded
    And messages are emitted to RH and Action Scheduler with <questionnaire type> questionnaire types
    When set action rule of type "<action type>" when the case loading queues are drained
    And CE Estab messages are emitted to RH and Action Scheduler with <individual qid type> questionnaire types
    Then correctly formatted "<pack code>" print files are created for CE Estab expected responses
    And there is a correct "<pack code>" manifest file for each csv file written
    And the expected number of "RM_UAC_CREATED" and [PRINT_CASE_SELECTED,SAMPLE_LOADED] events are logged against the case
    And the files have all been copied to the bucket

    Examples: CE Estab initial contact Letters: <pack code>
      | pack code   | action type | questionnaire type | sample file                   | individual qid type |
      | D_ICA_ICLR1 | CE_IC03     | 31                 | sample_3_english_CE_estab.csv | 21                  |

    @regression
    Examples: CE Estab initial contact Letters: <pack code>
      | pack code    | action type | questionnaire type | sample file                       | individual qid type |
      | D_ICA_ICLR2B | CE_IC04     | 32                 | sample_3_welsh_CE_estab.csv       | 22                  |
      | D_CE4A_ICLR4 | CE_IC05     | 34                 | sample_3_ni_CE_estab_resident.csv | 24                  |
      | D_CE4A_ICLS4 | CE_IC06     | 34                 | sample_3_ni_CE_estab_student.csv  | 24                  |


  Scenario Outline: Generate print files and log events for initial contact questionnaires
    Given sample file "<sample file>" is loaded
    And messages are emitted to RH and Action Scheduler with <questionnaire types> questionnaire types
    When set action rule of type "<action type>" when the case loading queues are drained
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
    Given sample file "<sample file>" is loaded
    And messages are emitted to RH and Action Scheduler with <questionnaire types> questionnaire types
    When set action rule of type "<action type>" when the case loading queues are drained
    And CE Estab messages are emitted to RH and Action Scheduler with <individual qid type> questionnaire types
    Then correctly formatted "<pack code>" print files are created for CE Estab questionnaires
    And there is a correct "<pack code>" manifest file for each csv file written
    And the expected number of "RM_UAC_CREATED" and [PRINT_CASE_SELECTED,SAMPLE_LOADED] events are logged against the case

    Examples: CE Estab Initial contact questionnaire: <pack code>
      | pack code | action type | questionnaire types | sample file                            | individual qid type |
      | D_FDCE_I4 | CE_IC08     | [34]                | sample_3_ni_CE_estab_questionnaire.csv | 24                  |

    @regression
    Examples: CE Estab Initial contact questionnaire: <pack code>
      | pack code | action type | questionnaire types | sample file                                 | individual qid type |
      | D_FDCE_I1 | CE_IC09     | [31]                | sample_3_english_CE_estab_questionnaire.csv | 21                  |


  Scenario: Generate print files and log events for Welsh CE initial contact questionnaires
    Given sample file "sample_3_welsh_CE_estab_questionnaire.csv" is loaded
    And messages are emitted to RH and Action Scheduler with [32] questionnaire types
    When set action rule of type "CE_IC10" when the case loading queues are drained
    And CE Estab messages are emitted to RH and Action Scheduler with [22,23] questionnaire types
    Then correctly formatted "D_FDCE_I2" print files are created for CE Estab Welsh questionnaires
    And there is a correct "D_FDCE_I2" manifest file for each csv file written
    And two "RM_UAC_CREATED" events [PRINT_CASE_SELECTED,SAMPLE_LOADED] are logged per case


  Scenario Outline: Generate print files and log events for scheduled reminder letters
    Given sample file "<sample file>" is loaded
    When set action rule of type "<pack code>" when the case loading queues are drained
    And messages are emitted to RH and Action Scheduler with <questionnaire types> questionnaire types
    When UAC Updated events emitted for the <number of matching cases> cases with matching treatment codes
    Then correctly formatted "<pack code>" reminder letter print files are created
    And there is a correct "<pack code>" manifest file for each csv file written
    And "PRINT_CASE_SELECTED" events are logged against the cases included in the reminder

    Examples: Reminder letter: <pack code>
      | pack code   | questionnaire types | number of matching cases | sample file                          |
      | P_RL_1RL1_1 | [01]                | 2                        | sample_input_england_census_spec.csv |

    @regression
    Examples: Reminder letter: <pack code>
      | pack code     | questionnaire types | number of matching cases | sample file                        |
      | P_RL_2RL2B_3a | [02]                | 2                        | sample_input_wales_census_spec.csv |


  Scenario Outline:  Generate print files and log events for scheduled questionnaire letters
    Given sample file "<sample file>" is loaded successfully
    And set action rule of type "<pack code>" when the case loading queues are drained
    When 2 UAC Updated events are emitted for the <number of matching cases> cases with matching treatment codes
    Then correctly formatted "<pack code>" reminder questionnaire print files are created
    And there is a correct "<pack code>" manifest file for each csv file written
    And "PRINT_CASE_SELECTED" events are logged against the cases included in the reminder

    Examples: Initial contact questionnaire: <pack code>
      | pack code | number of matching cases | sample file                           |
      | P_QU_H2   | 3                        | sample_for_reminder_questionnaire.csv |


  Scenario Outline:  Generate print files and log events for response driven reminders
    Given sample file "<sample file>" is loaded successfully
    When set action rule of type "<pack code>" when the case loading queues are drained
    When UAC Updated events emitted for the <number of matching cases> cases with matching treatment codes
    Then correctly formatted "<pack code>" reminder letter print files are created
    And there is a correct "<pack code>" manifest file for each csv file written
    And "PRINT_CASE_SELECTED" events are logged against the cases included in the reminder

    Examples: Reminder contact letter: <pack code>
      | pack code   | number of matching cases | sample file                                        |
      | P_RD_2RL1_1 | 3                        | sample_input_england_response_driven_reminders.csv |

    @regression
    Examples: Reminder contact letter: <pack code>
      | pack code    | number of matching cases | sample file                                        |
      | P_RD_2RL2B_1 | 1                        | sample_input_wales_census_spec.csv                 |
      | P_RD_2RL1_2  | 2                        | sample_input_england_response_driven_reminders.csv |
      | P_RD_2RL2B_2 | 2                        | sample_input_wales_census_spec.csv                 |
      | P_RD_2RL1_3  | 1                        | sample_input_england_response_driven_reminders.csv |
      | P_RD_2RL2B_3 | 1                        | sample_input_wales_census_spec.csv                 |
