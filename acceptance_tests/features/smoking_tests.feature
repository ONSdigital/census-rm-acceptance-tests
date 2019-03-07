Feature: Smoke tests to check the system is tied together correctly

  @SmokeTest
  Scenario: Successful sample file upload
      Given a survey exists with a collection exercise
      When sample file "Sample_10.csv" is loaded
      Then the the correctly formatted files are created on the sftp server