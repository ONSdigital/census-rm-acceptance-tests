Feature: Print files for initial contact letters can be generated and uploaded

  Scenario Outline: Generate print files and log events for initial contact letters
    Given an action rule of type "<action type>" is set 2 seconds in the future
    When sample file "<sample file>" is loaded
    Then messages are emitted to RH and Action Scheduler with <questionnaire types> questionnaire types
    And correctly formatted "<pack code>" print files are created
    And there is a correct "<pack code>" manifest file for each csv file written
    And events logged against the case are [PRINT_CASE_SELECTED,SAMPLE_LOADED]

    Examples: Initial contact letter: <pack code>
      | pack code  | action type | questionnaire types | sample file                          |
      | P_IC_ICL1  | ICL1E       | [01]                | sample_input_england_census_spec.csv |
      | P_IC_ICL2B | ICL2W       | [02]                | sample_input_wales_census_spec.csv   |
      | P_IC_ICL4  | ICL4N       | [04]                | sample_input_ni_census_spec.csv      |
