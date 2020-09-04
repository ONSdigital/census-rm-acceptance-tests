Feature: Internal messages used by RM which might be used by future systems

  Scenario: A DEACTIVATE_UAC msg is sent and processed
    Given sample file "sample_1_english_HH_unit.csv" is loaded successfully
    When a deactivate uac msg is sent for each uac emitted
    Then UAC_UPDATED msgs with active set to false for all the original uacs created
    And every created UAC QID pair has a DEACTIVATE_UAC event logged against it

  Scenario: Address Update
    Given sample file "sample_1_english_HH_unit.csv" is loaded successfully
    When an RM address update message is sent
    Then CASE_UPDATED event is emitted with updated case data
    And a CREATE message is sent to field for each updated case excluding NI CE cases and estab types "TRANSIENT PERSONS" and "MIGRANT WORKERS"

