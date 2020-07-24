# Created by adamhawtin at 23/07/2020
Feature: Bulk refusal CSV files can be processed

  Scenario: A bulk refusal file is successfully ingested
    Given sample file "sample_for_print_stories.csv" is loaded successfully
    And a bulk refusal file is supplied
    When the bulk refusal file is processed
    Then the cases are marked with the correct refusal