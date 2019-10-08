Feature: Handle CCS (Census Coverage Survey) Property Listed events

  Scenario: Log event when a CCS Property Listed event is received
    When a CCS Property Listed event is sent
    Then the CCS Property Listed case is created
    And the correct ActionInstruction is sent to FWMT
    And the case API returns the CCS QID for the new case