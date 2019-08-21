Feature: Print files for initial contact questionnaires can be generated and uploaded

    Scenario: Successful sample file upload and England ICQ print file
    Given an action rule of type "ICHHQE" is set 2 seconds in the future
    When sample file "sample_input_census_spec_england_questionnaire.csv" is loaded
    Then messages are emitted to RH and Action Scheduler with [01] questionnaire types
    And correctly formatted "P_IC_H1" print files are created for questionnaire
    And there is a correct "P_IC_H1" manifest file for each csv file written
    And events logged against the case are [PRINT_CASE_SELECTED,SAMPLE_LOADED]

  Scenario: Successful sample file upload and Wales ICQ print file
    Given an action rule of type "ICHHQW" is set 2 seconds in the future
    When sample file "sample_input_census_spec_wales_questionnaire.csv" is loaded
    Then messages are emitted to RH and Action Scheduler with [02,03] questionnaire types
    And correctly formatted "P_IC_H2" print files are created for questionnaire
    And there is a correct "P_IC_H2" manifest file for each csv file written
    And events logged against the case are [PRINT_CASE_SELECTED,SAMPLE_LOADED]

  Scenario: Successful sample file upload and NI ICQ print file
    Given an action rule of type "ICHHQN" is set 2 seconds in the future
    When sample file "sample_input_census_spec_ni_questionnaire.csv" is loaded
    Then messages are emitted to RH and Action Scheduler with [04] questionnaire types
    And correctly formatted "P_IC_H4" print files are created for questionnaire
    And there is a correct "P_IC_H4" manifest file for each csv file written
    And events logged against the case are [PRINT_CASE_SELECTED,SAMPLE_LOADED]