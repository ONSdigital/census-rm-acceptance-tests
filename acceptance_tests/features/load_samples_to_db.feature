Feature: Load Samples from file to database

  Background: Clear DB
    Given the database is cleared down

  Scenario: Good sample file load GSFL
    Given there is a live collection exercise with unique id "GSFL"
    When a sample file "10RowSampleFile.csv" is loaded
    Then "10" Rows appear on the case database

