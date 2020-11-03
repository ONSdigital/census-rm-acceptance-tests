Feature: Field Case Updated Events

  Scenario: A request to change the CE expected capacity for a case and a cancel message is sent to field
    Given sample file "sample_1_english_CE_unit.csv" is loaded successfully
    When a Field Case Updated message has been sent with expected capacity as "0"
    Then a case_updated msg is emitted where "ceExpectedCapacity" is "0"
    And the events logged for the case are [SAMPLE_LOADED,FIELD_CASE_UPDATED]
    And a CANCEL action instruction is sent to field work management with address type "CE"

  Scenario: A request to change the CE expected capacity for a case and a cancel message is not sent to field
    Given sample file "sample_1_english_CE_unit.csv" is loaded successfully
    When a Field Case Updated message has been sent with expected capacity as "3"
    Then a case_updated msg is emitted where "ceExpectedCapacity" is "3"
    And the events logged for the case are [SAMPLE_LOADED,FIELD_CASE_UPDATED]
    And an UPDATE action instruction is sent to field work management with address type "CE"

  @regression
  Scenario: A request to change the CE expected capacity for a CE estab case isn't sent to field
    Given sample file "sample_1_english_CE_estab.csv" is loaded successfully
    When a Field Case Updated message has been sent with expected capacity as "0"
    Then a case_updated msg is emitted where "ceExpectedCapacity" is "0"
    And the events logged for the case are [SAMPLE_LOADED,FIELD_CASE_UPDATED]
    And no ActionInstruction is sent to FWMT
