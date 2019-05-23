@smoke_test
Feature: Smoke tests to check the system is tied together correctly

  Scenario: Successful sample file upload and England ICL print file
    Given an action rule of type ICL1E is set 10 seconds in the future
    When sample file "sample_input_england_census_spec.csv" is loaded
    Then messages are emitted to RH and Action Scheduler
    And correctly formatted "P_IC_ICL1" print files are created
    And there is a correct "P_IC_ICL1" manifest file for each csv file written

  Scenario: Successful sample file upload and Wales ICL print file
    Given an action rule of type ICL2E is set 10 seconds in the future
    When sample file "sample_input_wales_census_spec.csv" is loaded
    Then messages are emitted to RH and Action Scheduler
    And correctly formatted "P_IC_ICL2" print files are created
    And there is a correct "P_IC_ICL2" manifest file for each csv file written

  Scenario: Successful sample file upload and Wales ICQ print file
    Given an action rule of type ICHHQW is set 10 seconds in the future
    When sample file "sample_input_census_spec_wales_questionnaire.csv" is loaded
    Then messages are emitted to RH and Action Scheduler for wales questionnaire
    And correctly formatted "P_IC_H2" print files are created for wales questionnaire
    And there is a correct "P_IC_H2" manifest file for each csv file written

