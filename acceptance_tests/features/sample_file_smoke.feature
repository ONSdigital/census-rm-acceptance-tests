@smoke_test
Feature: Smoke tests to check the system is tied together correctly

  Scenario: Successful sample file upload
      Given a survey exists with a collection exercise
      And an action rule of type ICL1E is set 10 seconds in the future
      When sample file "sample_input_census_spec.csv" is loaded
      Then the sample units are created and stored in the case service
      And correctly formatted print files are created
      And there is a correct manifest file for each csv file written
