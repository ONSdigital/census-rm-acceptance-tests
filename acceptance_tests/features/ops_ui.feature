Feature: Finding cases on R-ops UI

  Scenario: Finding cases via postcode
    Given sample file "postcode_search_13_cases.csv" is loaded successfully
    And a user is on the r-ops-ui home page ready to search
    When a user searches for cases by postcode
    Then the cases are presented to the user in order

  Scenario: Seeing all case details
    Given sample file "sample_1_english_HH_unit.csv" is loaded successfully
    When a user navigates to the case details page for the chosen case
    Then the user can see all case details for the chosen case

  Scenario: RM_UAC_CREATED event is not visible on case details page
    Given sample file "sample_1_english_HH_unit.csv" is loaded successfully
    And a UAC fulfilment request "UACHHT1" message for a created case is sent
    When a user navigates to the case details page for the chosen case
    Then the user can see all case details for the chosen case except for the RM_UAC_CREATED event