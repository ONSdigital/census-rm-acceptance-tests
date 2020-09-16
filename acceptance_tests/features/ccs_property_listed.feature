Feature: Handle CCS (Census Coverage Survey) Property Listed events

  Scenario: Log event when a CCS Property Listed event is received with interview required true
    When a CCS Property Listed event is sent with interview required set to True
    Then the CCS Property Listed case is created with address type "HH"
    And the correct ActionInstruction is sent to FWMT
    And the case API returns the CCS QID for the new case
    And the case API returns the new CCS case by postcode search


  Scenario: Log event when a CCS Property Listed event is received with interview required false
    When a CCS Property Listed event is sent with interview required set to False
    Then the CCS Property Listed case is created with address type "HH"
    And no ActionInstruction is sent to FWMT
    And the case API returns the CCS QID for the new case
    And the case API returns the new CCS case by postcode search