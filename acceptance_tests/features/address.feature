Feature: Address updates

  Scenario: Invalid address
    Given sample file "sample_for_questionnaire_linked.csv" is loaded
    And messages are emitted to RH and Action Scheduler with [01] questionnaire types
    When an invalid address message is sent from "CC"
    Then a case_updated msg is emitted where "addressInvalid" is "True"
    And an ActionCancelled event is sent to field work management
    And the case event log records invalid address
