Feature: Handle CCS (Census Coverage Survey) Property Listed events

  Scenario: Log event when a CCS Property Listed event is received
    When a CCS Property Listed event is sent
    Then the CCS Property Listed case is created