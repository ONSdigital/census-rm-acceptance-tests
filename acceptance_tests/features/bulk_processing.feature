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
    And every created case has a DEACTIVATE_UAC event logged against it

  Scenario: A DEACTIVATE_UAC msg is sent and processed
    Given sample file "sample_for_print_stories.csv" is loaded successfully
    When a deactivate uac msg is sent for each uac emitted
    Then UAC_UPDATED msgs with active set to false for all the original uacs created
    And every created case has a DEACTIVATE_UAC event logged against it
