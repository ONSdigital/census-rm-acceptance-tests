Feature: Internal messages used by RM which might be used by future systems

  Scenario: Address Update
    Given sample file "sample_1_english_HH_unit.csv" is loaded successfully
    When an RM address update message is sent
    Then CASE_UPDATED event is emitted with updated case data
