Feature: Internal messages used by RM from bulk processing actions

  Scenario: A DEACTIVATE_UAC msg is sent and processed
    Given sample file "sample_1_english_HH_unit_with_fieldcoordinator.csv" is loaded successfully
    When a deactivate uac msg is sent for each uac emitted
    Then UAC_UPDATED msgs with active set to false for all the original uacs created
    And every created UAC QID pair has a DEACTIVATE_UAC event logged against it

  Scenario: Address Update for addresses already known to field
    Given sample file "sample_1_english_HH_unit_with_fieldcoordinator.csv" is loaded successfully
    When an RM address update message is sent
    Then CASE_UPDATED event is emitted with updated case data
    And an UPDATE message is sent to field for each updated case excluding NI CE, "TRANSIENT PERSONS" and refused

  Scenario: Address update for addresses previously unknown to field
    Given sample file "sample_for_new_address_updates.csv" is loaded successfully
    When an RM address update message is sent
    Then CASE_UPDATED event is emitted with updated case data
    And a CREATE message is sent to field for each updated case excluding NI CE cases and estab types "TRANSIENT PERSONS" and "MIGRANT WORKERS"

  Scenario: Un-invalidate an address message is sent
    Given sample file "sample_1_english_HH_unit_with_fieldcoordinator.csv" is loaded successfully
    And all the cases are marked as invalid
    When an UNINVALIDATE_ADDRESS message is sent
    Then CASE_UPDATED events are emitted for all the cases
    And an UPDATE message is sent to field for each updated case excluding NI CE, "TRANSIENT PERSONS" and refused

  Scenario: NonCompliance message is sent
    Given sample file "sample_1_english_HH_unit.csv" is loaded successfully
    When a non compliance message is sent
    Then a case updated event is emitted with nonCompliance set
