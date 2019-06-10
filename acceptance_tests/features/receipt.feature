
Feature: Case processor handles receipt message from pubsub service
  Case LogEvent set on our system (can we test for this now)

  Scenario: eQ receipt results in UAC updated event sent to RH
    Given sample file "sample_for_receipting.csv" is loaded
    Then messages are emitted to RH and Action Scheduler for with [01] qids
    When the receipt msg for the created case is put on the GCP pubsub
    Then a uac_updated msg is emitted with active set to false
