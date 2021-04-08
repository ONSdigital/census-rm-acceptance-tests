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

  Scenario: We deliver some mail to the wrong place for a skeleton case with no FieldCoordinatorId
    Given a NEW_ADDRESS_REPORTED event with no FieldCoordinatorId with address type "HH" is sent from "CC"
    When an undelivered mail PPO message is put on GCP pubsub
    And the events logged for the receipted case are [NEW_ADDRESS_REPORTED,UNDELIVERED_MAIL_REPORTED]
    And no ActionInstruction is sent to FWMT

  Scenario: Unaddressed material is returned as UAA with being linked to a case
    Given an unaddressed QID request message of questionnaire type 01 is sent
    And a UAC updated message with "01" questionnaire type is emitted
    When an undelivered mail QM message for the unlinked QID is put on GCP pubsub
    Then the events logged for the unaddressed QID are [UAC_UPDATED,UNDELIVERED_MAIL_REPORTED]
