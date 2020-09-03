Feature: Finding cases on R-ops UI

  Scenario: Finding cases via postcode
    Given sample file "sample_2_english_units_postcode_search.csv" is loaded successfully
    And a user is on the r-ops-ui home page ready to search
    When a user searches for cases via postcode
    Then the cases are returned to the user

  Scenario: CE U cases are grouped with parent CE E case
    Given sample file "sample_7_english_ce_cases_postcode_search.csv" is loaded successfully
    And a user is on the r-ops-ui home page ready to search
    When a user searches for cases via postcode
    Then the cases are returned to the user in a sensible order

  Scenario: Seeing all case details
    Given sample file "sample_1_english_HH_unit.csv" is loaded successfully
    When a user has searched for cases
    Then the user can see all case details for chosen case

  Scenario: RM_UAC_CREATED event is not visible on case details page
    Given sample file "sample_1_english_HH_unit.csv" is loaded successfully
    And a UAC fulfilment request "UACHHT1" message for a created case is sent
    When a user has searched for cases
    Then the user can see all case details for chosen case except for the RM_UAC_CREATED event