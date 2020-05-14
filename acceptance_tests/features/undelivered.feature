Feature: We want to deliver mail to the wrong addresses

  @smoke
  Scenario: We deliver some mail to the wrong place and QM knows about it
    Given sample file "sample_for_receipting.csv" is loaded successfully
    When an undelivered mail QM message is put on GCP pubsub
    And a case_updated msg is emitted where the metadata field "causeEventType" is "UNDELIVERED_MAIL_REPORTED"
    And the events logged for the receipted case are [SAMPLE_LOADED,UNDELIVERED_MAIL_REPORTED]
    And an ActionRequest event is sent to field work management

  Scenario: We deliver some mail to the wrong place and PPO knows about it
    Given sample file "sample_for_receipting.csv" is loaded successfully
    When an undelivered mail PPO message is put on GCP pubsub
    And a case_updated msg is emitted where the metadata field "causeEventType" is "UNDELIVERED_MAIL_REPORTED"
    And the events logged for the receipted case are [SAMPLE_LOADED,UNDELIVERED_MAIL_REPORTED]
    And an ActionRequest event is sent to field work management
