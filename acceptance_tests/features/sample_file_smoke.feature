Feature: Checks that input sample files and action rules results in correct print files and emitted msgs

  Scenario: Successful sample file upload and England ICL print file
    Given an action rule of type ICL1E is set 10 seconds in the future
    When sample file "sample_input_england_census_spec.csv" is loaded
    Then messages are emitted to RH and Action Scheduler for with 1 qid per sample
    And correctly formatted "P_IC_ICL1" print files are created
    And there is a correct "P_IC_ICL1" manifest file for each csv file written

  Scenario: Successful sample file upload and Wales ICL print file
    Given an action rule of type ICL2W is set 10 seconds in the future
    When sample file "sample_input_wales_census_spec.csv" is loaded
    Then messages are emitted to RH and Action Scheduler for with 1 qid per sample
    And correctly formatted "P_IC_ICL2" print files are created
    And there is a correct "P_IC_ICL2" manifest file for each csv file written

  Scenario: Successful sample file upload and NI ICL print file
    Given an action rule of type ICL4N is set 10 seconds in the future
    When sample file "sample_input_ni_census_spec.csv" is loaded
    Then messages are emitted to RH and Action Scheduler for with 1 qid per sample
    And correctly formatted "P_IC_ICL4" print files are created
    And there is a correct "P_IC_ICL4" manifest file for each csv file written

  Scenario: Successful sample file upload and England ICQ print file
    Given an action rule of type ICHHQE is set 10 seconds in the future
    When sample file "sample_input_census_spec_england_questionnaire.csv" is loaded
    Then messages are emitted to RH and Action Scheduler for with 1 qid per sample
    And correctly formatted "P_IC_H1" print files are created for questionnaire
    And there is a correct "P_IC_H1" manifest file for each csv file written

  Scenario: Successful sample file upload and Wales ICQ print file
    Given an action rule of type ICHHQW is set 10 seconds in the future
    When sample file "sample_input_census_spec_wales_questionnaire.csv" is loaded
   Then messages are emitted to RH and Action Scheduler for with 2 qid per sample
    And correctly formatted "P_IC_H2" print files are created for questionnaire
    And there is a correct "P_IC_H2" manifest file for each csv file written

  Scenario: Successful sample file upload and NI ICQ print file
    Given an action rule of type ICHHQN is set 10 seconds in the future
    When sample file "sample_input_census_spec_ni_questionnaire.csv" is loaded
    Then messages are emitted to RH and Action Scheduler for with 1 qid per sample
    And correctly formatted "P_IC_H4" print files are created for questionnaire
    And there is a correct "P_IC_H4" manifest file for each csv file written
