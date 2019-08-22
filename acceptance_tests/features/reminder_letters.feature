Feature: Print files for reminder letters can be generated and uploaded

  Scenario Outline: Generate print files and log events for scheduled reminder letters
    Given sample file "<sample file>" is loaded
    And an action rule of type "<pack code>" is set 2 seconds in the future
    And messages are emitted to RH and Action Scheduler with <questionnaire types> questionnaire types
    When UAC Updated events for the new reminder UAC QID pairs are emitted for the <number of matching cases> cases with matching treatment codes
    Then correctly formatted "<pack code>" reminder letter print files are created
    And there is a correct "<pack code>" manifest file for each csv file written
    And "PRINT_CASE_SELECTED" events are logged against the cases included in the reminder

    Examples: Reminder letter: <pack code>
      | pack code     | questionnaire types | number of matching cases | sample file                          |
      | P_RL_1RL1_1   | [01]                | 2                        | sample_input_england_census_spec.csv |
      | P_RL_2RL2B_3a | [02]                | 2                        | sample_input_wales_census_spec.csv   |