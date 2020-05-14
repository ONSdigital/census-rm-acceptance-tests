@smoke
Feature: Case look up for the contact centre

  Scenario: Find case by caseId
    Given sample file "sample_input_england_census_spec.csv" is loaded successfully
    Then a case can be retrieved from the case API service

  Scenario: Find multiple cases from a single UPRN
    Given sample file "sample_input_england_census_spec.csv" is loaded successfully
    Then case API returns multiple cases for a UPRN

  Scenario: Find case by caseRef
    When sample file "sample_input_england_census_spec.csv" is loaded successfully
    Then a case can be retrieved by its caseRef

  Scenario: Check case-api returns correct fields for a CENSUS case
    Given sample file "sample_1_english_HH_unit.csv" is loaded successfully
    Then a case can be retrieved from the case API service
    And it contains the correct fields for a CENSUS case

  Scenario: Check case-api returns correct fields for a CCS case
    When a CCS Property Listed event is sent
    Then the CCS Property Listed case is created with address type "HH"
    And it contains the correct fields for a CCS case