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

  Scenario: A bulk deactivate uac file is successfully ingested
    Given sample file "sample_for_print_stories.csv" is loaded successfully
    And a bulk deactivate uac file is supplied
    When the bulk deactivate file is processed
    Then UAC_UPDATED msgs with active set to false for all the original uacs created
    And every created UAC QID pair has a DEACTIVATE_UAC event logged against it

  Scenario: A bulk address update file is successfully ingested
    Given sample file "HH_unit_and_NI_CE_unit.csv" is loaded successfully
    And a bulk address update file is supplied
    When the bulk address update file is processed
    Then CASE_UPDATED events are emitted for all the updated cases with correctly updated data and skeleton marker false
    And the cases are updated in the database
    And a CREATE message is sent to field for each updated case excluding NI CE cases and estab types "TRANSIENT PERSONS" and "MIGRANT WORKERS"

  Scenario: A bulk address update file for a skeleton case is successfully ingested
    Given a NEW_ADDRESS_REPORTED event with address type "HH" is sent from "FIELD" and the case is created
    And a bulk address update file is supplied
    When the bulk address update file is processed
    Then CASE_UPDATED events are emitted for all the updated cases with correctly updated data and skeleton marker false
    And the cases are updated in the database
    And a CREATE message is sent to field for each updated case excluding NI CE cases and estab types "TRANSIENT PERSONS" and "MIGRANT WORKERS"

  Scenario: A bulk address un-invalidate file is successfully ingested
    Given sample file "sample_input_wales_census_spec.csv" is loaded successfully
    And all the cases are marked as invalid
    And a bulk un-invalidate addresses file is supplied
    When the bulk un-invalidate address file is processed
    Then CASE_UPDATED events are emitted for all the cases in the file with addressInvalid false
    And the addresses for the cases are un-invalidated in the database
    And an UPDATE message is sent to field for each updated case excluding NI CE, estab type "TRANSIENT PERSONS"
