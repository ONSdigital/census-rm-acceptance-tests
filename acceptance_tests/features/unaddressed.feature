Feature: Generating UAC/QID pairs for unaddressed letters & questionnaires

  Scenario: UAC/QID pair generated for unaddressed
    When an unaddressed QID request message of questionnaire type 01 is sent
    Then a UACUpdated message not linked to a case is emitted to RH and Action Scheduler

  Scenario: Questionnaire linked to unaddressed
    Given sample file "sample_for_questionnaire_linked.csv" is loaded successfully
    When an unaddressed QID request message of questionnaire type 01 is sent
    And a UACUpdated message not linked to a case is emitted to RH and Action Scheduler
    And a Questionnaire Linked message is sent
    Then a Questionnaire Linked event is logged

  Scenario: Questionnaire linked to unaddressed CCS case
    Given a CCS Property Listed event is sent
    And the CCS Property Listed case is created with address type "HH"
    When an unaddressed QID request message of questionnaire type 01 is sent
    And a UACUpdated message not linked to a case is emitted to RH and Action Scheduler
    And a Questionnaire Linked message is sent for the CCS case
    Then a Questionnaire Linked event is logged

  Scenario: Individual Questionnaire linked to unaddressed
    Given sample file "sample_for_questionnaire_linked.csv" is loaded successfully
    When an unaddressed QID request message of questionnaire type 21 is sent
    And a UACUpdated message not linked to a case is emitted to RH and Action Scheduler
    And an Individual Questionnaire Linked message is sent and ingested
    Then a Questionnaire Linked event is logged
    And the HI individual case can be retrieved

  Scenario: Individual Questionnaire linked to unaddressed without specifying individual case ID
    Given sample file "sample_for_questionnaire_linked.csv" is loaded successfully
    When an unaddressed QID request message of questionnaire type 21 is sent
    And a UACUpdated message not linked to a case is emitted to RH and Action Scheduler
    And an Individual Questionnaire Linked message with no individual case ID is sent and ingested
    Then a Questionnaire Linked event is logged
    And the HI individual case can be retrieved

  Scenario: Receipt of unlinked unaddressed
    When an unaddressed QID request message of questionnaire type 01 is sent
    And a UACUpdated message not linked to a case is emitted to RH and Action Scheduler
    And a receipt for the unlinked UAC-QID pair is received
    Then message redelivery does not go bananas

  Scenario: Unlinked QID is relinked to new case
    Given sample file "sample_for_questionnaire_linked.csv" is loaded successfully
    When an unaddressed QID request message of questionnaire type 01 is sent
    And a UACUpdated message not linked to a case is emitted to RH and Action Scheduler
    And a Questionnaire Linked message is sent
    And a Questionnaire Linked event is logged
    And a Questionnaire Linked message is sent to relink to a new case
    Then a Questionnaire Linked event is logged
    And a Questionnaire Unlinked event is logged

  @smoke
  @local-docker
  Scenario: Correct print files generated
    When the unaddressed batch is loaded, the print files are generated
