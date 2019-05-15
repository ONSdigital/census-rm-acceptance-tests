
Feature: EQ receipt results in uac updated event sent to RH
  Case LogEvent set on our system (can we test for this now)

  Scenario:
    Given sample file "sample_for_receipting.csv" is loaded
    When the a receipt msg for the case is put on the GCP pubsub
    Then the QID UAC pairs are emitted to Respondent Home