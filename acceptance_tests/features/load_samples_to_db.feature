Feature: Load Samples from file to database

  Scenario: Successful sample file upload
    Given a survey exists with collection exercise
    When a sample file "Sample_10.csv" is loaded
    Then a call to the casesvc api returns 10 cases

