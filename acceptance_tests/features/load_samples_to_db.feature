Feature: Load Samples from file to database

  Background: Clear DB
    Given the database is cleared down

  Scenario: Good sample file load GSFL
    Given there is a live collection exercise with unique id "GSFL"
    When a sample file "Sample_10.csv" is loaded
    Then a call to the casesvc api returns 10 cases

