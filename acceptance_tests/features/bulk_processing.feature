@regression
Feature: Bulk event CSV files can be processed

  Scenario: A bulk refusal file is successfully ingested
    Given sample file "sample_input_wales_census_spec.csv" is loaded successfully
    And a bulk refusal file is supplied
    When the bulk refusal file is processed
    Then the cases are marked with the correct refusal

  Scenario: A bulk new address file is successfully ingested
    Given a bulk new address file "new_addresses_33.csv" is supplied
    When the bulk new address file is processed
    Then CASE_CREATED events are emitted for all the new addressed supplied
    And the new address cases are ingested into the database

  Scenario: A bulk invalid address file is successfully ingested
    Given sample file "sample_input_wales_census_spec.csv" is loaded successfully
    And a bulk invalid address file is supplied
    When the bulk invalid address file is processed
    Then CASE_UPDATED events are emitted for all the cases in the file with addressInvalid true

  Scenario: A bulk address update file is successfully ingested
    Given sample file "sample_1_english_HH_unit.csv" is loaded successfully
    And a bulk address update file is supplied
    When the bulk address update file is processed
    Then CASE_UPDATED events are emitted for all the updated cases with correctly updated data and skeleton marker false

  Scenario: A bulk address update file for a skeleton case is successfully ingested
    Given a NEW_ADDRESS_REPORTED event with address type "HH" is sent from "FIELD" and the case is created
    And a bulk address update file is supplied
    When the bulk address update file is processed
    Then CASE_UPDATED events are emitted for all the updated cases with correctly updated data and skeleton marker false
