Feature: Scheduled reminder print and manifest files can be generated and uploaded

  Scenario Outline: Generate print files and log events for scheduled reminder letters
    Given sample file "<sample file>" is loaded successfully
    When we schedule an action rule of type "<pack code>"
    Then UAC Updated events are emitted for the <no matching cases> cases with matching treatment codes with questionnaire type "<questionnaire type>"
    And correctly formatted "<pack code>" reminder letter print files are created
    And there is a correct "<pack code>" manifest file for each csv file written
    And "PRINT_CASE_SELECTED" events are logged against the cases included in the reminder

    Examples: Reminder letter: <pack code>
      | pack code   | no matching cases | questionnaire type | sample file                          |
      | P_RL_1RL1_1 | 2                 | 01                 | sample_input_england_census_spec.csv |

    @regression
    Examples: Reminder letter: <pack code>
      | pack code    | no matching cases | questionnaire type | sample file                                       |
      | P_RL_1RL2B_1 | 2                 | 02                 | sample_input_wales_uac_census_spec.csv            |
      | P_RL_2RL4    | 2                 | 04                 | sample_input_ni_2nd_reminder_census_spec.csv      |
      | P_RL_3RL2B   | 1                 | 02                 | sample_input_wales_3rd_reminder_census_spec.csv   |
      | P_RL_3RL1    | 2                 | 01                 | sample_input_england_3rd_reminder_census_spec.csv |
      | P_RL_2RL1    | 2                 | 01                 | sample_input_england_2nd_reminder_census_spec.csv |
      | P_RL_1RL1B   | 1                 | 01                 | sample_input_england_reminder_b_census_spec.csv   |


  # Note that in practice these actions will be run with the reminder batch scheduler
  Scenario: Generate print files and log events for welsh scheduled reminder questionnaire letters
    Given sample file "sample_for_reminder_questionnaire.csv" is loaded successfully
    When we schedule an action rule of type "P_QU_H2"
    Then 2 UAC Updated events are emitted for the 3 cases with matching treatment codes
    And correctly formatted "P_QU_H2" reminder questionnaire print files are created
    And there is a correct "P_QU_H2" manifest file for each csv file written
    And "PRINT_CASE_SELECTED" events are logged against the cases included in the reminder

  @regression
  Scenario Outline: Generate print files and log events for scheduled reminder questionnaire letters
    Given sample file "<sample file>" is loaded successfully
    When we schedule an action rule of type "<pack code>"
    Then UAC Updated events are emitted for the <number of matching cases> cases with matching treatment codes with questionnaire type "<questionnaire type>"
    And correctly formatted "<pack code>" reminder questionnaire print files are created
    And there is a correct "<pack code>" manifest file for each csv file written
    And "PRINT_CASE_SELECTED" events are logged against the cases included in the reminder

    Examples: Reminder questionnaire: <pack code>
      | pack code | number of matching cases | questionnaire type | sample file        |
      | P_QU_H4   | 1                        | 04                 | HH_unit_1ALSFN.csv |

      # Note that in practice these actions will be run with the reminder batch scheduler
      | P_QU_H1   | 1                        | 01                 | HH_unit_LP1E.csv   |

  Scenario Outline: Generate print files and log events for response driven reminders
    Given sample file "<sample file>" is loaded successfully
    When we schedule an action rule of type "<pack code>" for LSOAs <LSOAs>
    Then UAC Updated events are emitted for the <number of matching cases> cases with matching treatment codes with questionnaire type "<questionnaire type>"
    Then correctly formatted "<pack code>" reminder letter print files are created
    And there is a correct "<pack code>" manifest file for each csv file written
    And "PRINT_CASE_SELECTED" events are logged against the cases included in the reminder

    Examples: Reminder contact letter: <pack code>
      | pack code  | LSOAs                      | number of matching cases | questionnaire type | sample file                           |
      | P_RD_RNP41 | ('E01014540', 'E01014541') | 2                        | 01                 | response_driven_reminders_england.csv |

    @regression
    Examples: Reminder contact letter: <pack code>
      | pack code   | LSOAs         | number of matching cases | questionnaire type | sample file                           |
      | P_RD_RNP42B | ('W01014669', 'W01014897') | 2                        | 02                 | sample_input_wales_census_spec.csv    |
      | P_RD_RNP51  | ('E01014545', 'E01014547') | 2                        | 01                 | response_driven_reminders_england.csv |
      | P_RD_RNP52B | ('W01033361', 'W01014540') | 2                        | 02                 | sample_input_wales_census_spec.csv    |


  Scenario Outline: Generate print files and log events for scheduled reminders with no uac and survey launched
    Given sample file "<sample file>" is loaded successfully
    And we receive a survey launch event for some of the cases
    When we schedule an action rule of type "<pack code>"
    Then correctly formatted "<pack code>" print files with no uac are created for pack code where survey launched
    And there is a correct "<pack code>" manifest file for each csv file written

    Examples: Reminder contact letter: <pack code>
      | pack code  | sample file                                  |
      | P_RL_1RL4A | sample_input_ni_1st_reminder_census_spec.csv |

    @regression
    Examples: Reminder contact letter: <pack code>
      | pack code   | sample file          |
      | P_RL_1RL1A  | HH_units_england.csv |
      | P_RL_1RL2BA | HH_units_wales.csv   |
      | P_RL_2RL1A  | HH_units_england.csv |
      | P_RL_2RL2BA | HH_units_wales.csv   |

  Scenario Outline: Generate print files and log events for scheduled reminders with new uac and survey launched
    Given sample file "<sample file>" is loaded successfully
    When we schedule an action rule of type "<pack code>"
    Then UAC Updated events are emitted for the 1 cases with matching treatment codes with questionnaire type "<questionnaire type>"
    And correctly formatted "<pack code>" reminder letter print files are created
    And there is a correct "<pack code>" manifest file for each csv file written

    Examples: Reminder contact letter: <pack code>
      | pack code  | questionnaire type | sample file      |
      | P_RL_1RL1B | 01                 | HH_unit_QP3E.csv |

    @regression
    Examples: Reminder contact letter: <pack code>
      | pack code   | questionnaire type | sample file                                    |
      | P_RL_1RL2BB | 02                 | HH_unit_QP3W.csv                               |
      | P_RL_1RL4   | 04                 | sample_1_input_ni_1st_reminder_census_spec.csv |


  Scenario Outline: Generate print files and log events for scheduled reminder letters checking for MILITARY SFA
    Given sample file "<sample file>" is loaded successfully
    When set SPG MILITARY SFA action rule of type "<pack code>" when the case loading queues are drained
    And UAC Updated events are emitted for the <number of matching cases> cases with matching treatment codes with questionnaire type "<questionnaire type>"
    Then correctly formatted "<pack code>" reminder letter print files are created
    And there is a correct "<pack code>" manifest file for each csv file written
    And "PRINT_CASE_SELECTED" events are logged against the cases included in the reminder

    Examples: Reminder letter: <pack code>
      | pack code   | number of matching cases | questionnaire type | sample file                           |
      | P_RL_1RL1_1 | 2                        | 01                 | sample_2_english_SPG_MILITARY_SFA.csv |


  Scenario Outline: Individual response reminder for HI cases created by EQ IR SMS request
    Given sample file "<sample file>" is loaded successfully
    And an individual SMS UAC fulfilment request "<fulfilment code>" message is sent by EQ
    And an EQ individual response HI case created and uac updated event are emitted
    When the individual response reminder action rule of type "<reminder pack code>" is set
    Then correctly formatted "<reminder pack code>" individual reminder letter print files are created
    And there is a correct "<reminder pack code>" manifest file for each csv file written

    Examples: Individual Response Reminder letter: <reminder pack code>
      | reminder pack code | fulfilment code | sample file                  |
      | P_RL_1IRL1         | UACIT1          | sample_1_english_HH_unit.csv |

    @regression
    Examples: Individual Response Reminder letter: <reminder pack code>
      | reminder pack code | fulfilment code | sample file                |
      | P_RL_1IRL2B        | UACIT2          | sample_1_welsh_HH_unit.csv |
      | P_RL_1IRL2B        | UACIT2W         | sample_1_welsh_HH_unit.csv |


  @regression
  Scenario Outline: Individual response reminder for HI cases created by EQ IR print request
    Given sample file "<sample file>" is loaded successfully
    And an individual print UAC fulfilment request "<fulfilment code>" message is sent by EQ
    And an EQ individual response HI case created and uac updated event are emitted
    When the individual response reminder action rule of type "<reminder pack code>" is set
    Then correctly formatted "<reminder pack code>" individual reminder letter print files are created
    And there is a correct "<reminder pack code>" manifest file for each csv file written

    Examples: Individual Response Reminder letter: <reminder pack code>
      | reminder pack code | fulfilment code | sample file                  |
      | P_RL_1IRL1         | P_UAC_UACIP1    | sample_1_english_HH_unit.csv |
      | P_RL_1IRL2B        | P_UAC_UACIP2B   | sample_1_welsh_HH_unit.csv   |


  Scenario Outline: Generate print files and log events for scheduled reminder letters checking for non compliance
    Given sample file "<sample file>" is loaded successfully
    And a bulk noncompliance file is supplied
    And the bulk noncompliance file is processed
    When we schedule an action rule of type "<pack code>" with NCL and "<region>" classifiers
    Then correctly formatted "<pack code>" reminder letter print files are created for cases marked non compliance
    And there is a correct "<pack code>" manifest file for each csv file written

    Examples: Reminder letter: <pack code>
      | pack code    | region | sample file                  |
      | P_NC_NCLTA1  | E      | HH_units_england.csv |
      | P_NC_NCLTA2B | W      | HH_units_wales.csv   |