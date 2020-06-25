Feature: Handle CCS (Census Coverage Survey) Property Listed events

  Scenario: Log event when a CCS Property Listed event is received with no qid
    When a CCS Property Listed event is sent
    Then the CCS Property Listed case is created with address type "HH"
    And the correct ActionInstruction is sent to FWMT
    And the case API returns the CCS QID for the new case
    And the case API returns the new CCS case by postcode search

  @smoke
  Scenario: Log event when a CCS Property Listed event is received with a qid
    When an unaddressed QID request message of questionnaire type 71 is sent and an unlinked uac is emitted
    When a CCS Property Listed event is sent with a qid
    Then the CCS Property Listed case is created with address type "HH"
    And no ActionInstruction is sent to FWMT
    And the case API returns the new CCS case by postcode search

  Scenario: CCS Listed with refusal
    When a CCS Property Listed event is sent with refusal
    Then the CCS Property Listed case is created with address type "HH"
    And the CCS case listed event is logged
    And no ActionInstruction is sent to FWMT
    And the case API returns the CCS QID for the new case
    And the case API returns the new CCS case by postcode search

  Scenario: CCS Listed with Address invalid
    When a CCS Property Listed event is sent with an address invalid event and address type "NR"
    Then the CCS Property Listed case is created with address type "NR"
    And the CCS case listed event is logged
    And no ActionInstruction is sent to FWMT
    And the case API returns the CCS QID for the new case
    And the case API returns the new CCS case by postcode search
