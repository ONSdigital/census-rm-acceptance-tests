@smoke_test
Feature: Tests that cover unaddressed scenarios

  Scenario: UAC/QID pair generated for unaddressed
    Given the unaddressed batch is run
    When an unaddressed message of questionnaire type 01 is sent
    Then a UACUpdated message not linked to a case is emitted to RH and Action Scheduler
