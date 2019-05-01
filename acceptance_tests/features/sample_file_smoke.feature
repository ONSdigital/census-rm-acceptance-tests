@smoke_test
Feature: Smoke tests to check the system is tied together correctly

  Scenario: Successful sample file upload
    Given an action rule of type ICL1E is set 10 seconds in the future
    When sample file "sample_input_census_spec.csv" is loaded
    Then messages are emitted to RH and Action Scheduler
    And correctly formatted print files are created
    And there is a correct manifest file for each csv file written