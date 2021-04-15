Feature: Handle CCS (Census Coverage Survey) Property Listed events

  Scenario Outline: Log event when a CCS Property Listed event is received with interview required true
    When a CCS Property Listed event with address type "<address type>" and estab type "<estab type>" is sent with interview required set to True
    Then the CCS Property Listed case is created with address type "<address type>"
    And the correct ActionInstruction is sent to FWMT
    And the case API returns the CCS QID for the new case with form type "H"
    And the case API returns the new CCS case with case type "<address type>" by postcode search

    Examples:
      | address type | estab type |
      | HH           | HOUSEHOLD  |
      | CE           | HOTEL      |

  Scenario Outline: Log event when a CCS Property Listed event is received with interview required false
    When a CCS Property Listed event with address type "<address type>" and estab type "<estab type>" is sent with interview required set to False
    Then the CCS Property Listed case is created with address type "<address type>"
    And no ActionInstruction is sent to FWMT
    And the case API returns the CCS QID for the new case with form type "H"
    And the case API returns the new CCS case with case type "<address type>" by postcode search

    Examples:
      | address type | estab type |
      | HH           | HOUSEHOLD  |
      | CE           | HOTEL      |
      | NR           | HOUSEHOLD  |
