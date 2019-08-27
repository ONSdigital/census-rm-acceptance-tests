Feature: Case processor handles receipt message from pubsub service
  Case LogEvent set on our system

  Scenario: eQ receipt results in UAC updated event sent to RH
    Given sample file "sample_for_receipting.csv" is loaded
    And messages are emitted to RH and Action Scheduler with [01] questionnaire types
    When the receipt msg for the created case is put on the GCP pubsub
    Then a uac_updated msg is emitted with active set to false
    And a case_updated msg is emitted where "receiptReceived" is "True"
    And an ActionCancelled event is sent to field work management
    And the events logged for the receipted case are [SAMPLE_LOADED,RESPONSE_RECEIVED]

  Scenario: eQ receipt results in UAC updated event sent to RH, simulate missing case_id
    Given sample file "sample_for_receipting.csv" is loaded
    And messages are emitted to RH and Action Scheduler with [01] questionnaire types
    When the receipt msg for the created case is put on the GCP pubsub with just qid
    Then a uac_updated msg is emitted with active set to false
    And a case_updated msg is emitted where "receiptReceived" is "True"
    And an ActionCancelled event is sent to field work management
    And the events logged for the receipted case are [SAMPLE_LOADED,RESPONSE_RECEIVED]

  Scenario: Receipted Cases are excluded from print files
    Given an action rule of type "ICL1E" is set 10 seconds in the future
    And sample file "sample_input_england_census_spec.csv" is loaded
    And messages are emitted to RH and Action Scheduler with [01] questionnaire types
    When the receipt msg for a created case is put on the GCP pubsub
    Then only unreceipted cases appear in "P_IC_ICL1" print files
    And a case_updated msg is emitted where "receiptReceived" is "True"
    And the events logged for the receipted case are [SAMPLE_LOADED,RESPONSE_RECEIVED]
