Feature: Case look up for the contact centre

  Scenario: Find case by caseId
    Given sample file "sample_input_england_census_spec.csv" is loaded
    Then messages are emitted to RH and Action Scheduler with [01] questionnaire types
    And a case can be retrieved from the case API service

  Scenario: Find multiple cases from a single UPRN
    Given sample file "sample_input_england_census_spec.csv" is loaded
    Then messages are emitted to RH and Action Scheduler with [01] questionnaire types
    And case API returns multiple cases for a UPRN

  Scenario: Find case by caseRef
    When sample file "sample_input_england_census_spec.csv" is loaded
    Then messages are emitted to RH and Action Scheduler with [01] questionnaire types
    And a case can be retrieved by its caseRef

  Scenario: Check non-existent caseId returns a 404 status code
    Given a random caseId is generated
    Then case API should return a 404 when queried

  Scenario: Check non-existent uprn returns a 404 status code
    Given a random uprn is generated
    Then case API should return a 404 when queried

  Scenario: Check non-existent caseRef returns a 404 status code
    Given a random caseRef is generated
    Then case API should return a 404 when queried

  Scenario: Check case-api returns correct fields for a CENSUS case
    Given sample file "sample_1_english_unit.csv" is loaded
    Then messages are emitted to RH and Action Scheduler with [01] questionnaire types
    Then a case can be retrieved from the case API service
    And it contains the correct fields for a CENSUS case

  Scenario: Check case-api returns correct fields for a CCS case
    When a CCS Property Listed event is sent
    Then the CCS Property Listed case is created with case_type "HH"
    And it contains the correct fields for a CCS case