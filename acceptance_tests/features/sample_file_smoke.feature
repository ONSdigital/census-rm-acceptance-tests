@smoke_test
Feature: Smoke tests to check the system is tied together correctly

  Scenario: Successful sample file upload
      Given a survey exists with a collection exercise
      When sample file "Sample_10.csv" is loaded
      Then the sample units are created and stored in the case service
      And correctly formatted notification files are created