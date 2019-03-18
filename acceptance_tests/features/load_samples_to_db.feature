Feature: Load Samples from file to database

  Scenario: Successful sample file upload
    Given a survey exists with a collection exercise
    When sample file "sample_input_census_spec.csv" is loaded
    Then the sample units are created and stored in the case service
