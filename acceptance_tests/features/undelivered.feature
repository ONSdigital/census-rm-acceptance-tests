Feature: We want to deliver mail to the wrong addresses

  Scenario: We deliver some mail to the wrong place and QM knows about it
    Given sample file "sample_for_receipting.csv" is loaded
    And messages are emitted to RH and Action Scheduler with [01] questionnaire types
    When an undelivered mail QM message is put on GCP pubsub
    And a case_updated msg is emitted where "undeliveredAsAddressed" is "True"
    And the events logged for the receipted case are [SAMPLE_LOADED,UNDELIVERED_MAIL_REPORTED]
    And an ActionRequest event is sent to field work management

  Scenario: We deliver some mail to the wrong place and PPO knows about it
    Given sample file "sample_for_receipting.csv" is loaded
    And messages are emitted to RH and Action Scheduler with [01] questionnaire types
    When an undelivered mail PPO message is put on GCP pubsub
    And a case_updated msg is emitted where "undeliveredAsAddressed" is "True"
    And the events logged for the receipted case are [SAMPLE_LOADED,UNDELIVERED_MAIL_REPORTED]
    And an ActionRequest event is sent to field work management