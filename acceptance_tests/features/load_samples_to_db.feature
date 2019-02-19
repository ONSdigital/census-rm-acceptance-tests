Feature: Load Samples from file to database

  Scenario: Good sample file load GSFL
    Given a survey exists
    And a collection exercise exists in a scheduled state
    And a Social Notification action plan exists
    When a sample file "Sample_10.csv" is loaded
    Then a call to the casesvc api returns 10 cases

