Feature: Print files for initial contact letters can be generated and uploaded

  Scenario: Successful sample file upload and England ICL print file
    Given an action rule of type "ICL1E" is set 2 seconds in the future
    When sample file "sample_input_england_census_spec.csv" is loaded
    Then messages are emitted to RH and Action Scheduler with [01] questionnaire types
    And correctly formatted "P_IC_ICL1" print files are created
    And there is a correct "P_IC_ICL1" manifest file for each csv file written
    And events logged against the case are [PRINT_CASE_SELECTED,SAMPLE_LOADED]

  Scenario: Successful sample file upload and Wales ICL print file
    Given an action rule of type "ICL2W" is set 2 seconds in the future
    When sample file "sample_input_wales_census_spec.csv" is loaded
    Then messages are emitted to RH and Action Scheduler with [02] questionnaire types
    And correctly formatted "P_IC_ICL2B" print files are created
    And there is a correct "P_IC_ICL2B" manifest file for each csv file written
    And events logged against the case are [PRINT_CASE_SELECTED,SAMPLE_LOADED]

  Scenario: Successful sample file upload and NI ICL print file
    Given an action rule of type "ICL4N" is set 2 seconds in the future
    When sample file "sample_input_ni_census_spec.csv" is loaded
    Then messages are emitted to RH and Action Scheduler with [04] questionnaire types
    And correctly formatted "P_IC_ICL4" print files are created
    And there is a correct "P_IC_ICL4" manifest file for each csv file written
    And events logged against the case are [PRINT_CASE_SELECTED,SAMPLE_LOADED]