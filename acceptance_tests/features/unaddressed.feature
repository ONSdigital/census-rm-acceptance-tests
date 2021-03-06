Feature: Generating UAC/QID pairs for unaddressed letters & questionnaires

  Scenario: UAC/QID pair generated for unaddressed
    When an unaddressed QID request message of questionnaire type 01 is sent
    Then a UACUpdated message not linked to a case is emitted to RH and Action Scheduler

  @smoke
  @local-docker
  Scenario: Correct print files generated
    When the unaddressed batch is loaded, the print files are generated
