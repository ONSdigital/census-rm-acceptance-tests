Feature: Bulk event CSV files can be processed

  Scenario: A bulk refusal file is successfully ingested
    Given sample file "sample_for_print_stories.csv" is loaded successfully
    And a bulk refusal file is supplied
    When the bulk refusal file is processed
    Then the cases are marked with the correct refusal

  Scenario: A bulk new address file is successfully ingested
    Given a bulk new address file is supplied
    When the bulk new address file is processed
    Then CASE_CREATED events are emitted for all the new addressed supplied