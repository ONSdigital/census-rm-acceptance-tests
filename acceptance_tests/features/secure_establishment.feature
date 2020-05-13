Feature: Handle Secure Establishments

  @smoke
  Scenario: Marking a case as secureEstablishment is reflected in RM
    Given sample file "sample_1_english_CE_secure_estab.csv" is loaded successfully
    When a FIELD action rule for address type "CE" is set when loading queues are drained
    Then the case can be retrieved from the case API service and has a secureEstablishment value of "true"
    And the action instruction is emitted to FWMT where case has a secureEstablishment value of "true"

  Scenario: Marking a case as not secureEstablishment is reflected in RM
    Given sample file "sample_1_english_CE_estab.csv" is loaded successfully
    When a FIELD action rule for address type "CE" is set when loading queues are drained
    Then the case can be retrieved from the case API service and has a secureEstablishment value of "false"
    And the action instruction is emitted to FWMT where case has a secureEstablishment value of "false"

  Scenario: Marking a case as secureEstablishment is reflected in RM
    Given sample file "sample_1_english_SPG_secure_estab.csv" is loaded successfully
    When a FIELD action rule for address type "SPG" is set when loading queues are drained
    Then the case can be retrieved from the case API service and has a secureEstablishment value of "true"
    And the action instruction is emitted to FWMT where case has a secureEstablishment value of "true"
