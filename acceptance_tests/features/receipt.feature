
Feature: EQ receipt results in uac updated event sent to RH
  Case LogEvent set on our system (can we test for this now)

  Scenario:
    Given sample file "sample_for_receipting.csv" is loaded
    When the receipt msg for the created case is put on the GCP pubsub
    Then a uac_updated msg is emitted with active set to false