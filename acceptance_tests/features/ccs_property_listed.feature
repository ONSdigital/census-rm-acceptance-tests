Feature: Handle CCS (Census Coverage Survey) Property Listed events

  Scenario: Log event when a CCS Property Listed event is received with no qid
    When a CCS Property Listed event is sent
    Then the CCS Property Listed case is created with case_type "HH"
    And the correct ActionInstruction is sent to FWMT
    And the case API returns the CCS QID for the new case

  Scenario: Log event when a CCS Property Listed event is received with a qid
    When an unaddressed message of questionnaire type 71 is sent
    And a UACUpdated message not linked to a case is emitted to RH and Action Scheduler
    When a CCS Property Listed event is sent with a qid
    And the CCS Property Listed case is created with case_type "HH"
    And no ActionInstruction is sent to FWMT

  Scenario: CCS Listed with refusal
    When a CCS Property Listed event is sent with refusal
    Then the CCS Property Listed case is created with case_type "HH"
    And the CCS case listed event is logged
    And no ActionInstruction is sent to FWMT
    And the case API returns the CCS QID for the new case

  Scenario: CCS Listed with Address invalid
    When a CCS Property Listed event is sent with an address invalid event and addressType "NR"
    Then the CCS Property Listed case is created with case_type "NR"
    And the CCS case listed event is logged
    And no ActionInstruction is sent to FWMT
    And the case API returns the CCS QID for the new case
