Feature: Load Samples from file to database

  Scenario: Successful sample file upload Welsh questionnaire
    Given sample file "sample_input_census_spec_wales_questionnaire.csv" is loaded
    Then the new cases are emitted to Respondent Home
    And two Wales QID UAC pairs are emitted to Respondent Home
