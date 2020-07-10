Feature: Scheduled reminder print and manifest files can be generated and uploaded

  Scenario Outline: Generate print files and log events for scheduled reminder letters
    Given sample file "<sample file>" is loaded and correct qids <questionnaire types> set
    When set action rule of type "<pack code>"
    Then UAC Updated events emitted for the 2 cases with matching treatment codes
    And correctly formatted "<pack code>" reminder letter print files are created
    And there is a correct "<pack code>" manifest file for each csv file written
    And "PRINT_CASE_SELECTED" events are logged against the cases included in the reminder

    Examples: Reminder letter: <pack code>
      | pack code   | questionnaire types | sample file                          |
      | P_RL_1RL1_1 | [01]                | sample_input_england_census_spec.csv |

    @regression
    Examples: Reminder letter: <pack code>
      | pack code     | questionnaire types | sample file                        |
      | P_RL_2RL2B_3a | [02]                | sample_input_wales_census_spec.csv |

  Scenario Outline: Generate print files and log events for scheduled reminder letters
    Given sample file "<sample file>" is loaded and correct qids <questionnaire types> set
    When set action rule of type "<pack code>"
    Then UAC Updated events emitted for the 2 cases with matching treatment codes
    And correctly formatted "<pack code>" reminder letter print files are created
    And there is a correct "<pack code>" manifest file for each csv file written
    And "PRINT_CASE_SELECTED" events are logged against the cases included in the reminder

    Examples: Reminder letter: <pack code>
      | pack code   | questionnaire types | sample file                          |
      | P_RL_1RL1_1 | [01]                | sample_input_england_census_spec.csv |

    @regression
    Examples: Reminder letter: <pack code>
      | pack code     | questionnaire types | sample file                        |
      | P_RL_2RL2B_3a | [02]                | sample_input_wales_census_spec.csv |

  Scenario: Generate print files and log events for scheduled reminder questionnaire letters
    Given sample file "sample_for_reminder_questionnaire.csv" is loaded successfully
    When set action rule of type "P_QU_H2"
    Then 2 UAC Updated events are emitted for the 3 cases with matching treatment codes
    And correctly formatted "P_QU_H2" reminder questionnaire print files are created
    And there is a correct "P_QU_H2" manifest file for each csv file written
    And "PRINT_CASE_SELECTED" events are logged against the cases included in the reminder


  Scenario Outline: Generate print files and log events for response driven reminders
    Given sample file "<sample file>" is loaded successfully
    When set action rule of type "<pack code>"
    Then UAC Updated events emitted for the <number of matching cases> cases with matching treatment codes
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


  Scenario Outline: Generate print files and log events for response driven reminders with survey started
    Given sample file "<sample file>" is loaded successfully
    And a survey launched for a created case is received for cases with lsoa <lsoa list>
    When set action rule of type "<pack code>"
    Then correctly formatted "<pack code>" print files are created for packcode and where survey was launched
    And there is a correct "<pack code>" manifest file for each csv file written

    Examples: Reminder contact letter: <pack code>
      | pack code   | lsoa list                                 | sample file                                        |
      | P_RL_1RL1A  | [E01014540,E01014541]                     | sample_input_england_response_driven_reminders.csv |

    @regression
    Examples: Reminder contact letter: <pack code>
      | pack code   | lsoa list                                 | sample file                                        |
      | P_RL_1RL2BA | [E01014669,W01014669]                     | sample_input_wales_census_spec.csv                 |
      | P_RL_2RL1A  | [E01014543,E01014544]                     | sample_input_england_response_driven_reminders.csv |
      | P_RL_2RL2BA | [E01033361,E01015005,W01033361,W01015005] | sample_input_wales_census_spec.csv                 |


  Scenario Outline: Generate print files and log events for scheduled reminder letters checking for MILITARY SFA
    Given sample file "<sample file>" is loaded successfully
    When set SPG MILITARY SFA action rule of type "<pack code>" when the case loading queues are drained
    And UAC Updated events emitted for the <number of matching cases> cases with matching treatment codes
    Then correctly formatted "<pack code>" reminder letter print files are created
    And there is a correct "<pack code>" manifest file for each csv file written
    And "PRINT_CASE_SELECTED" events are logged against the cases included in the reminder

    Examples: Reminder letter: <pack code>
      | pack code   | number of matching cases | sample file                           |
      | P_RL_1RL1_1 | 1                        | sample_1_english_SPG_MILITARY_SFA.csv |


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


  Scenario Outline: Individual response reminder for HI cases created by EQ IR print request
    Given sample file "<sample file>" is loaded successfully
    And an individual print UAC fulfilment request "<fulfilment code>" message is sent by EQ
    And an EQ individual response HI case created and uac updated event are emitted
    When the individual response reminder action rule of type "<reminder pack code>" is set
    Then correctly formatted "<reminder pack code>" individual reminder letter print files are created
    And there is a correct "<reminder pack code>" manifest file for each csv file written

    @regression
    Examples: Individual Response Reminder letter: <reminder pack code>
      | reminder pack code | fulfilment code | sample file                  |
      | P_RL_1IRL1         | P_UAC_UACIP1    | sample_1_english_HH_unit.csv |
      | P_RL_1IRL2B        | P_UAC_UACIP2B   | sample_1_welsh_HH_unit.csv   |
