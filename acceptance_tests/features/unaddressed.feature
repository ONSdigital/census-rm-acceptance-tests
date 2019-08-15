Feature: Generating UAC/QID pairs for unaddressed letters & questionnaires

  Scenario: UAC/QID pair generated for unaddressed
    When an unaddressed message of questionnaire type 01 is sent
    Then a UACUpdated message not linked to a case is emitted to RH and Action Scheduler

  Scenario: Questionnaire linked to case
    Given sample file "sample_for_questionnaire_linked.csv" is loaded
    And messages are emitted to RH and Action Scheduler with [01] qids
    When the receipt msg for a created case is put on the GCP pubsub
    And a Questionnaire Linked message is sent
    Then a Questionnaire Linked event is logged
    And a CaseUpdated message is emitted to RH and Action Scheduler

  @local-docker
  Scenario: Correct print files generated
    When the unaddressed batch is loaded, the print files are generated