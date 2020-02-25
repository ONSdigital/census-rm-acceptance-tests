Feature: We want to deliver mail to the wrong addresses

  Scenario: We deliver some mail to the wrong place and QM knows about it
    Given sample file "sample_for_receipting.csv" is loaded successfully
    When an undelivered mail QM message is put on GCP pubsub
    Then a case_updated msg is emitted where "undeliveredAsAddressed" is "True"
    And the events logged for the receipted case are [SAMPLE_LOADED,UNDELIVERED_MAIL_REPORTED]
    And an ActionRequest event is sent to field work management

  Scenario: We deliver some mail to the wrong place and PPO knows about it
    Given sample file "sample_for_receipting.csv" is loaded successfully
    When an undelivered mail PPO message is put on GCP pubsub
    Then a case_updated msg is emitted where "undeliveredAsAddressed" is "True"
    And the events logged for the receipted case are [SAMPLE_LOADED,UNDELIVERED_MAIL_REPORTED]
    And an ActionRequest event is sent to field work management

  Scenario: We deliver some mail to the wrong CCS address and PPO knows about it
    Given a CCS Property Listed event is sent
    And the CCS Property Listed case is created with case_type "HH"
    And the correct ActionInstruction is sent to FWMT
    When an undelivered mail PPO message is put on GCP pubsub for the CCS case
    Then a case_updated msg is emitted where "undeliveredAsAddressed" is "True"
    And the events logged for the receipted case are [CCS_ADDRESS_LISTED,UNDELIVERED_MAIL_REPORTED]
    And an ActionRequest event is sent to field work management  
