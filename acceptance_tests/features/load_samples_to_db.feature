Feature: Load Samples from file to database

  Scenario: Successful sample file upload
    Given sample file "sample_input_census_spec.csv" is loaded
    Then the new cases are emitted to Respondent Home
    And the QID UAC pairs are emitted to Respondent Home
