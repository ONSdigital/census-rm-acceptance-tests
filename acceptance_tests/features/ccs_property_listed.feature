Feature: Handle CCS (Census Coverage Survey) Property Listed events

  Scenario: Log event when a CCS Property Listed event is received with no qid
    When a CCS Property Listed event is sent
    Then the CCS Property Listed case is created
    And the correct ActionInstruction is sent to FWMT

  Scenario: Log event when a CCS Property Listed event is received with a qid
    When an unaddressed message of questionnaire type 71 is sent
    And a UACUpdated message not linked to a case is emitted to RH and Action Scheduler
    When a CCS Property Listed event is sent with a qid
    And the CCS Property Listed case is created
    And no ActionInstruction is sent to FWMT
