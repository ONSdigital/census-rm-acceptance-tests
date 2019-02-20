Feature: Load Samples from file to database

  Scenario: Successful sample file upload
    Given a survey exists
    And a collection exercise exists in a scheduled state
    And a social action plan exists for the collection exercise
    When a sample file "Sample_10.csv" is loaded
    Then a call to the casesvc api returns 10 cases

