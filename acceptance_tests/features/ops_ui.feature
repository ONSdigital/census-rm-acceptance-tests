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

  Scenario: Linking a QID to a case
    Given sample file "sample_1_english_HH_unit.csv" is loaded successfully
    And an unaddressed QID request message of questionnaire type 01 is sent
    And a UAC updated message with "01" questionnaire type is emitted
    And a user navigates to the case details page for the chosen case
    When the user submits a QID to be linked to the case
    And the QID link confirmation page appears
    And the user confirms they wish to link the QID to be linked
    Then a QID link submitted message is flashed
    And a UAC_UPDATED message is emitted linking the submitted QID to the chosen case
    And the correct events are logged for the loaded case events "[SAMPLE_LOADED,UAC_UPDATED,QUESTIONNAIRE_LINKED]"

  Scenario: Attempting to link a bad qid to case
    Given sample file "sample_1_english_HH_unit.csv" is loaded successfully
    And a user navigates to the case details page for the chosen case
    When the user submits a bad QID to be linked to the case
    Then a failed to find QID message is flashed
