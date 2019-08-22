Feature: Print files for initial contact questionnaires can be generated and uploaded

  Scenario Outline: Generate print files and log events for initial contact letters
    Given an action rule of type "<action type>" is set 2 seconds in the future
    When sample file "<sample file>" is loaded
    Then messages are emitted to RH and Action Scheduler with <questionnaire types> questionnaire types
    And correctly formatted "<pack code>" print files are created for questionnaire
    And there is a correct "<pack code>" manifest file for each csv file written
    And events logged against the case are [PRINT_CASE_SELECTED,SAMPLE_LOADED]

    Examples: Initial contact questionnaire: <pack code>
      | pack code | action type | questionnaire types | sample file                                        |
      | P_IC_H1   | ICHHQE      | [01]                | sample_input_census_spec_england_questionnaire.csv |
      | P_IC_H2   | ICHHQW      | [02,03]             | sample_input_census_spec_wales_questionnaire.csv   |
      | P_IC_H4   | ICHHQN      | [04]                | sample_input_census_spec_ni_questionnaire.csv      |
