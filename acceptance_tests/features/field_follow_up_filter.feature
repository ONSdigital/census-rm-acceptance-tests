Feature: CN-80 Field Follow-up Filtering - Cases excluded from fieldwork

  Background:
    Given sample file "sample_input_england_census_spec.csv" is loaded successfully
    And an export file template has been created with template "P_IC_ICL1"
    And an export file action rule has been created for packcode "P_IC_ICL1"

  Scenario: Create message not sent when case marked as invalid
    Given a sample case is marked as invalid
    When a CASE_UPDATE event is emitted for the invalid case with fieldActionInstruction "CREATE"
    Then no fieldwork CREATE action message is sent for the case

  Scenario: Update message not sent when case marked as refused
    Given a sample case is marked as refused
    When a CASE_UPDATE event is emitted for the refused case with fieldActionInstruction "UPDATE"
    Then no fieldwork UPDATE action message is sent for the case
