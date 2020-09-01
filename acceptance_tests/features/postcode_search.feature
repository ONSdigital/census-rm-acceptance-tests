Feature: Finding cases via postcode on R-ops UI

  Scenario: Finding cases on r-ops ui via postcode
    Given sample file "sample_2_english_units_postcode_search.csv" is loaded successfully
    And a user is on the r-ops-ui home page ready to search
    When a user searches for cases via postcode
    Then the cases are returned to the user