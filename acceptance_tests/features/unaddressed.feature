Feature: Generating UAC/QID pairs for unaddressed letters & questionnaires
  Scenario: UAC/QID pair generated for unaddressed
    When an unaddressed message of questionnaire type 01 is sent
    Then a UACUpdated message not linked to a case is emitted to RH and Action Scheduler


  Scenario: Correct Print files generated
    Given I have the QID and UAC pairs ready
    When the print files are generated
    Then the print files contain the correct data
