Feature: Case look up for the contact centre

  Scenario: Find case by caseId
    Given sample file "sample_input_england_census_spec.csv" is loaded
    Then the new cases are emitted to Respondent Home
    And a case can be retrieved from the caseapi service

  Scenario: Check non-existent caseId returns an empty list
    Given a random caseId is generated
    Then caseapi should return an empty list when queried

  Scenario: Find multiple cases from a single UPRN
    Given sample file "sample_input_england_census_spec.csv" is loaded
    Then the new cases are emitted to Respondent Home
    And caseapi returns multiple cases for a UPRN

  Scenario: Find case by caseRef
    When sample file "sample_input_england_census_spec.csv" is loaded
    Then the new cases are emitted to Respondent Home
    And a case can be retrieved by its caseRef