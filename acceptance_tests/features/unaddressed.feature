Feature: Generating UAC/QID pairs for unaddressed letters & questionnaires

  Scenario: UAC/QID pair generated for unaddressed
    When an unaddressed message of questionnaire type 01 is sent
    Then a UACUpdated message not linked to a case is emitted to RH and Action Scheduler

  Scenario: Questionnaire linked to unaddressed
    Given sample file "sample_for_questionnaire_linked.csv" is loaded
    And messages are emitted to RH and Action Scheduler with [01] qids
    When a Questionnaire Linked message is received
    Then a UACUpdated message linked to a case is emitted to RH and Action Scheduler

  @local-docker
  Scenario: Correct print files generated
    When the unaddressed batch is loaded, the print files are generated