Feature: Case processor handles receipt message from pubsub service

  Scenario Outline: Receipted Cases increment ceActualResponses
    Given sample file "<sample file>" is loaded successfully
    And if required, a new qid and case are created for case type "<case type>" address level "<address level>" qid type "<qid type>" and country "<country>"
    When the receipt msg is put on the GCP pubsub
    Then a uac_updated msg is emitted with active set to false for the receipted qid
    And the correct events are logged for loaded case events "[<loaded case events>]" and individual case events "[<individual case events>]"
    And if the actual response count is incremented "<increment>" or the case is marked receipted "<receipt>" then there should be a case updated message of case type "<case type>"
    And if the field instruction "<instruction>" is not NONE a msg to field is emitted

    Examples:
      | case type | address level | qid type | increment | receipt | instruction | sample file                  | country | loaded case events                                                                      | individual case events           |
      | HH        | U             | HH       | False     | True    | CANCEL      | sample_1_english_HH_unit.csv | E       | SAMPLE_LOADED,RESPONSE_RECEIVED                                                         |                                  |
      | HH        | U             | Cont     | False     | False   | NONE        | sample_1_english_HH_unit.csv | E       | RESPONSE_RECEIVED,RM_UAC_CREATED,PRINT_CASE_SELECTED,FULFILMENT_REQUESTED,SAMPLE_LOADED |                                  |
      | HI        | U             | Ind      | False     | True    | NONE        | sample_1_english_HH_unit.csv | E       | FULFILMENT_REQUESTED,SAMPLE_LOADED                                                      | RESPONSE_RECEIVED,RM_UAC_CREATED |

    @regression
    Examples:
      | case type | address level | qid type | increment | receipt | instruction | sample file                   | country | loaded case events                                                                      | individual case events |
      | CE        | E             | Ind      | True      | False   | UPDATE      | sample_1_english_CE_estab.csv | E       | RESPONSE_RECEIVED,RM_UAC_CREATED,FULFILMENT_REQUESTED,SAMPLE_LOADED                     |                        |
      | CE        | E             | CE1      | False     | True    | UPDATE      | sample_1_english_CE_estab.csv | E       | SAMPLE_LOADED,RESPONSE_RECEIVED                                                         |                        |
      | CE        | U             | Ind      | True      | AR >= E | CANCEL      | sample_1_english_CE_unit.csv  | E       | RESPONSE_RECEIVED,RM_UAC_CREATED,FULFILMENT_REQUESTED,SAMPLE_LOADED                     |                        |
      | SPG       | E             | HH       | False     | False   | NONE        | sample_1_ni_SPG_estab.csv     | N       | SAMPLE_LOADED,RESPONSE_RECEIVED                                                         |                        |
      | SPG       | E             | Ind      | False     | False   | NONE        | sample_1_ni_SPG_estab.csv     | N       | RESPONSE_RECEIVED,RM_UAC_CREATED,FULFILMENT_REQUESTED,SAMPLE_LOADED                     |                        |
      | SPG       | U             | HH       | False     | True    | CANCEL      | sample_1_english_SPG_unit.csv | E       | SAMPLE_LOADED,RESPONSE_RECEIVED                                                         |                        |
      | SPG       | U             | Ind      | False     | False   | NONE        | sample_1_english_SPG_unit.csv | E       | RESPONSE_RECEIVED,RM_UAC_CREATED,FULFILMENT_REQUESTED,SAMPLE_LOADED                     |                        |
      | SPG       | U             | Cont     | False     | False   | NONE        | sample_1_english_SPG_unit.csv | E       | RESPONSE_RECEIVED,RM_UAC_CREATED,PRINT_CASE_SELECTED,FULFILMENT_REQUESTED,SAMPLE_LOADED |                        |


  Scenario: Receipted Cases are excluded from print files
    Given sample file "sample_input_england_census_spec.csv" is loaded successfully
    When the receipt msg for the created case is put on the GCP pubsub
    And set action rule of type "ICL1E" when case event "RESPONSE_RECEIVED" is logged
    Then only unreceipted cases appear in "P_IC_ICL1" print files
    And the events logged for the receipted case are [SAMPLE_LOADED,RESPONSE_RECEIVED]

  Scenario: Receipt of unaddressed continuation questionnaire does not send to Field
    Given an unaddressed QID request message of questionnaire type 63 is sent
    And a UACUpdated message not linked to a case is emitted to RH and Action Scheduler
    And a CCS Property Listed event is sent with a qid
    And the CCS Property Listed case is created with address type "HH"
    When the offline receipt msg for a continuation form from the case is received
    Then no ActionInstruction is sent to FWMT

  Scenario: eq receipt for CCS case results in UAC updated event sent to RH
    Given a CCS Property Listed event is sent
    And the CCS Property Listed case is created with address type "HH"
    And the correct ActionInstruction is sent to FWMT
    When the receipt msg for the created CCS case is put on the GCP pubsub
    Then a uac_updated msg is emitted with active set to false
    And a case_updated msg is emitted where "receiptReceived" is "True"
    And a CANCEL action instruction is sent to field work management with address type "HH"
    And the events logged for the receipted case are [CCS_ADDRESS_LISTED,RESPONSE_RECEIVED]

  @smoke
  Scenario: PQRS receipt results in UAC updated event sent to RH
    Given sample file "sample_for_receipting.csv" is loaded successfully
    When the offline receipt msg for the created case is put on the GCP pubsub
    Then a uac_updated msg is emitted with active set to false
    And a case_updated msg is emitted where "receiptReceived" is "True"
    And a CANCEL action instruction is sent to field work management with address type "HH"
    And the events logged for the receipted case are [SAMPLE_LOADED,RESPONSE_RECEIVED]

  Scenario: PQRS receipt for continuation questionnaire from fulfilment does not send to Field
    Given sample file "sample_for_receipting.csv" is loaded successfully
    And a PQ continuation fulfilment request event with fulfilment code "P_OR_HC1" is received by RM
    And a UAC updated message with "11" questionnaire type is emitted
    When the offline receipt msg for a continuation form from the case is put on the GCP pubsub
    Then a uac_updated msg is emitted with active set to false
    And the events logged for the receipted case are [SAMPLE_LOADED,FULFILMENT_REQUESTED,RM_UAC_CREATED,PRINT_CASE_SELECTED,RESPONSE_RECEIVED]
    And no ActionInstruction is sent to FWMT

  @regression
  Scenario: CE Actual response count incrementation continues after the case is receipted
    Given sample file "sample_1_english_CE_estab.csv" is loaded successfully
    And a new qid and case are created for case type "CE" address level "E" qid type "CE1" and country "E"
    And the receipt msg is put on the GCP pubsub
    And a uac_updated msg is emitted with active set to false for the receipted qid
    And an "UPDATE" field instruction is emitted
    And a case_updated msg is emitted where "receiptReceived" is "True"
    When a new qid and case are created for case type "CE" address level "E" qid type "Ind" and country "E"
    And the receipt msg is put on the GCP pubsub
    Then an "UPDATE" field instruction is emitted
    And if the actual response count is incremented "True" or the case is marked receipted "True" then there should be a case updated message of case type "CE"
