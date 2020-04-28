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
      | pack code      | action type | questionnaire types | sample file                          |
      | P_IC_ICL1      | ICL1E       | [01]                | sample_input_england_census_spec.csv |
      | P_IC_ICL2B     | ICL2W       | [02]                | sample_input_wales_census_spec.csv   |
      | P_IC_ICL4      | ICL4N       | [04]                | sample_input_ni_census_spec.csv      |
      | D_CE1A_ICLCR1  | CE1_IC01    | [31]                | sample_1_english_CE_estab.csv        |
      | D_CE1A_ICLCR2B | CE1_IC02    | [32]                | sample_1_welsh_CE_estab.csv          |
      | D_ICA_ICLR1    | CE_IC03_1   | [21]                | sample_1_english_CE_unit.csv         |
      | D_ICA_ICLR2B   | CE_IC04_1   | [22]                | sample_1_welsh_CE_unit.csv           |

  Scenario Outline: Generate print files and log events for initial contact letters CE Estabs
    Given sample file "<sample file>" is loaded
    And messages are emitted to RH and Action Scheduler with <questionnaire type> questionnaire types
    When set action rule of type "<action type>" when the case loading queues are drained
    And CE Estab messages are emitted to RH and Action Scheduler with <individual qid type> questionnaire types
    Then correctly formatted "<pack code>" print files are created for CE Estab expected responses
    And there is a correct "<pack code>" manifest file for each csv file written
    And expected number of uac events logged against the case are [PRINT_CASE_SELECTED,SAMPLE_LOADED]
    And the files have all been copied to the bucket

    Examples: CE Estab initial contact Letters: <pack code>
      | pack code    | action type | questionnaire type | sample file                   | individual qid type |
      | D_ICA_ICLR1  | CE_IC03     | 31                 | sample_3_english_CE_estab.csv | 21                  |
      | D_ICA_ICLR2B | CE_IC04     | 32                 | sample_3_welsh_CE_estab.csv   | 22                  |

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
      | P_IC_H4   | ICHHQN      | [04]                | sample_input_census_spec_ni_questionnaire.csv      |


  Scenario Outline: Generate print files and log events for scheduled reminder letters
    Given sample file "<sample file>" is loaded
    When set action rule of type "<pack code>" when the case loading queues are drained
    And messages are emitted to RH and Action Scheduler with <questionnaire types> questionnaire types
    When UAC Updated events emitted for the <number of matching cases> cases with matching treatment codes
    Then correctly formatted "<pack code>" reminder letter print files are created
    And there is a correct "<pack code>" manifest file for each csv file written
    And "PRINT_CASE_SELECTED" events are logged against the cases included in the reminder

    Examples: Reminder letter: <pack code>
      | pack code     | questionnaire types | number of matching cases | sample file                          |
      | P_RL_1RL1_1   | [01]                | 2                        | sample_input_england_census_spec.csv |
      | P_RL_2RL2B_3a | [02]                | 2                        | sample_input_wales_census_spec.csv   |


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
      | pack code    | number of matching cases | sample file                                        |
      | P_RD_2RL1_1  | 3                        | sample_input_england_response_driven_reminders.csv |
      | P_RD_2RL2B_1 | 1                        | sample_input_wales_census_spec.csv                 |
      | P_RD_2RL1_2  | 2                        | sample_input_england_response_driven_reminders.csv |
      | P_RD_2RL2B_2 | 2                        | sample_input_wales_census_spec.csv                 |
      | P_RD_2RL1_3  | 1                        | sample_input_england_response_driven_reminders.csv |
      | P_RD_2RL2B_3 | 1                        | sample_input_wales_census_spec.csv                 |



