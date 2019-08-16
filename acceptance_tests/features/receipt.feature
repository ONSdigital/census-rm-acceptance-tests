
Feature: Case processor handles receipt message from pubsub service
  Case LogEvent set on our system (can we test for this now)

  Scenario: eQ receipt results in UAC updated event sent to RH
    Given sample file "sample_for_receipting.csv" is loaded
    And messages are emitted to RH and Action Scheduler with [01] questionnaire types
    When the receipt msg for the created case is put on the GCP pubsub
    Then a uac_updated msg is emitted with active set to false
    And a case_updated msg is emitted where "receiptReceived" is "True"
    And a ActionCancelled event is sent to field work management
    And events logged for case are [SAMPLE_LOADED,RESPONSE_RECEIVED]

  Scenario: eQ receipt results in UAC updated event sent to RH, simulate missing case_id
    Given sample file "sample_for_receipting.csv" is loaded
    And messages are emitted to RH and Action Scheduler with [01] questionnaire types
    When the receipt msg for the created case is put on the GCP pubsub with just qid
    Then a uac_updated msg is emitted with active set to false
    And a case_updated msg is emitted where "receiptReceived" is "True"
    And a ActionCancelled event is sent to field work management
    And events logged for case are [SAMPLE_LOADED,RESPONSE_RECEIVED]