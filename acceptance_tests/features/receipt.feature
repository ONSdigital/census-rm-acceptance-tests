Feature: Case processor handles receipt message from pubsub service
  Case LogEvent set on our system

  Scenario: eQ receipt results in UAC updated event sent to RH
    Given sample file "sample_for_receipting.csv" is loaded successfully
    When the receipt msg for the created case is put on the GCP pubsub
    Then a uac_updated msg is emitted with active set to false
    And a case_updated msg is emitted where "receiptReceived" is "True"
    And an ActionCancelled event is sent to field work management
    And the events logged for the receipted case are [SAMPLE_LOADED,RESPONSE_RECEIVED]

  Scenario: eQ receipt results in UAC updated event sent to RH, simulate missing case_id
    Given sample file "sample_for_receipting.csv" is loaded successfully
    When the receipt msg for the created case is put on the GCP pubsub
    Then a uac_updated msg is emitted with active set to false
    And a case_updated msg is emitted where "receiptReceived" is "True"
    And an ActionCancelled event is sent to field work management
    And the events logged for the receipted case are [RESPONSE_RECEIVED,SAMPLE_LOADED]

  Scenario: PQRS receipt results in UAC updated event sent to RH
    Given sample file "sample_for_receipting.csv" is loaded successfully
    When the offline receipt msg for the created case is put on the GCP pubsub
    Then a uac_updated msg is emitted with active set to false
    And a case_updated msg is emitted where "receiptReceived" is "True"
    And an ActionCancelled event is sent to field work management
    And the events logged for the receipted case are [SAMPLE_LOADED,RESPONSE_RECEIVED]

  Scenario: PQRS receipt for continuation questionnaire from fulfilment does not send to Field
    Given sample file "sample_for_receipting.csv" is loaded successfully
    And a PQ continuation fulfilment request event with fulfilment code "P_OR_HC1" is received by RM
    And a UAC updated message with "11" questionnaire type is emitted
    When the offline receipt msg for a continuation form from the case is put on the GCP pubsub
    Then a uac_updated msg is emitted with active set to false
    And the events logged for the receipted case are [SAMPLE_LOADED,FULFILMENT_REQUESTED,RM_UAC_CREATED,PRINT_CASE_SELECTED,RESPONSE_RECEIVED]
    And no ActionInstruction is sent to FWMT

  Scenario: Receipt of unaddressed continuation questionnaire does not send to Field
    Given an unaddressed message of questionnaire type 63 is sent
    And a UACUpdated message not linked to a case is emitted to RH and Action Scheduler
    And a CCS Property Listed event is sent with a qid
    And the CCS Property Listed case is created with case_type "HH"
    When the offline receipt msg for a continuation form from the case is received
    Then no ActionInstruction is sent to FWMT

  Scenario: Receipted Cases are excluded from print files
    Given an action rule of type "ICL1E" is set 10 seconds in the future
    And sample file "sample_input_england_census_spec.csv" is loaded successfully
    When the receipt msg for the created case is put on the GCP pubsub
    Then only unreceipted cases appear in "P_IC_ICL1" print files
    And a case_updated msg is emitted where "receiptReceived" is "True"
    And the events logged for the receipted case are [SAMPLE_LOADED,RESPONSE_RECEIVED]
