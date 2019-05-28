Feature: Case look up for the contact centre

  Scenario: Find case by caseId
    Given sample file "sample_input_england_census_spec.csv" is loaded
    Then the new cases are emitted to Respondent Home
    And a case can be retrieved from the caseapi service

  Scenario: Find multiple cases from a single UPRN
    Given sample file "sample_input_england_census_spec.csv" is loaded
    Then the new cases are emitted to Respondent Home
    And caseapi returns multiple cases for a UPRN

  Scenario: Find case by caseRef
    When sample file "sample_input_england_census_spec.csv" is loaded
    Then the new cases are emitted to Respondent Home
    And a case can be retrieved by its caseRef

  Scenario: Check non-existent caseId returns a 404 status code
    Given a random caseId is generated
    Then caseapi should return a 404 when queried

  Scenario: Check non-existent uprn returns a 404 status code
    Given a random uprn is generated
    Then caseapi should return a 404 when queried

  Scenario: Check non-existent caseRef returns a 404 status code
    Given a random caseRef is generated
    Then caseapi should return a 404 when queried