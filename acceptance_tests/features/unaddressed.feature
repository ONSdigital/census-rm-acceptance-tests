Feature: Generating UAC/QID pairs for unaddressed letters & questionnaires

  Scenario: UAC/QID pair generated for unaddressed
    When an unaddressed message of questionnaire type 01 is sent
    Then a UACUpdated message not linked to a case is emitted to RH and Action Scheduler

  Scenario: Questionnaire linked to unaddressed
    Given sample file "sample_for_questionnaire_linked.csv" is loaded successfully
    When an unaddressed message of questionnaire type 01 is sent
    And a UACUpdated message not linked to a case is emitted to RH and Action Scheduler
    Then a Questionnaire Linked message is sent
    And a Questionnaire Linked event is logged

  Scenario: Individual Questionnaire linked to unaddressed
    Given sample file "sample_for_questionnaire_linked.csv" is loaded successfully
    When an unaddressed message of questionnaire type 21 is sent
    And a UACUpdated message not linked to a case is emitted to RH and Action Scheduler
    Then an Individual Questionnaire Linked message is sent
    And a Questionnaire Linked event is logged

  Scenario: Receipt of unlinked unaddressed
    Given an unaddressed message of questionnaire type 01 is sent
    And a UACUpdated message not linked to a case is emitted to RH and Action Scheduler
    When a receipt for the unlinked UAC-QID pair is received
    Then message redelivery does not go bananas

  @local-docker
  Scenario: Correct print files generated
    When the unaddressed batch is loaded, the print files are generated