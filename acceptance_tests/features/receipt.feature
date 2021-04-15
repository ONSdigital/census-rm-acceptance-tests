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
      | case type | address level | qid type | increment | receipt | instruction | sample file                             | country | loaded case events                                                  | individual case events           |
      | HH        | U             | HH       | False     | True    | CANCEL      | sample_1_english_HH_unit.csv            | E       | SAMPLE_LOADED,RESPONSE_RECEIVED                                     |                                  |
      | HI        | U             | Ind      | False     | True    | NONE        | sample_1_english_HH_unit.csv            | E       | FULFILMENT_REQUESTED,SAMPLE_LOADED                                  | RESPONSE_RECEIVED,RM_UAC_CREATED |
      | CE        | E             | CE1      | False     | True    | UPDATE      | sample_1_english_CE_estab.csv           | E       | SAMPLE_LOADED,RESPONSE_RECEIVED                                     |                                  |
      | CE        | U             | Ind      | True      | AR < E  | UPDATE      | sample_1_english_CE_unit_expected_2.csv | E       | RESPONSE_RECEIVED,RM_UAC_CREATED,FULFILMENT_REQUESTED,SAMPLE_LOADED |                                  |
      | CE        | U             | Ind      | True      | AR = E  | CANCEL      | sample_1_english_CE_unit.csv            | E       | RESPONSE_RECEIVED,RM_UAC_CREATED,FULFILMENT_REQUESTED,SAMPLE_LOADED |                                  |
      | SPG       | E             | HH       | False     | False   | NONE        | sample_1_ni_SPG_estab.csv               | N       | SAMPLE_LOADED,RESPONSE_RECEIVED                                     |                                  |
      | SPG       | U             | HH       | False     | True    | CANCEL      | sample_1_english_SPG_unit.csv           | E       | SAMPLE_LOADED,RESPONSE_RECEIVED                                     |                                  |
      | SPG       | U             | Ind      | False     | False   | NONE        | sample_1_english_SPG_unit.csv           | E       | RESPONSE_RECEIVED,RM_UAC_CREATED,FULFILMENT_REQUESTED,SAMPLE_LOADED |                                  |

    @regression
    Examples:
      | case type | address level | qid type | increment | receipt | instruction | sample file                             | country | loaded case events                                                                      | individual case events |
      | HH        | U             | CE1      | False     | False   | NONE        | sample_1_english_HH_unit.csv            | E       | RESPONSE_RECEIVED,SAMPLE_LOADED,QUESTIONNAIRE_LINKED,UAC_UPDATED                        |                        |
      | HH        | U             | Cont     | False     | False   | NONE        | sample_1_english_HH_unit.csv            | E       | RESPONSE_RECEIVED,RM_UAC_CREATED,PRINT_CASE_SELECTED,FULFILMENT_REQUESTED,SAMPLE_LOADED |                        |
      | HI        | U             | HH       | False     | True    | NONE        | sample_1_english_HH_unit.csv            | E       | SAMPLE_LOADED,FULFILMENT_REQUESTED                                                      |                        |
      | HI        | U             | CE1      | False     | False   | NONE        | sample_1_english_HH_unit.csv            | E       | SAMPLE_LOADED,FULFILMENT_REQUESTED                                                      |                        |
      | HI        | U             | Cont     | False     | False   | NONE        | sample_1_english_HH_unit.csv            | E       | RESPONSE_RECEIVED,RM_UAC_CREATED,PRINT_CASE_SELECTED,FULFILMENT_REQUESTED,SAMPLE_LOADED |                        |
      | CE        | E             | HH       | True      | False   | UPDATE      | sample_1_english_CE_estab.csv           | E       | RESPONSE_RECEIVED,SAMPLE_LOADED,QUESTIONNAIRE_LINKED,UAC_UPDATED                        |                        |
      | CE        | E             | Ind      | True      | False   | UPDATE      | sample_1_english_CE_estab.csv           | E       | RESPONSE_RECEIVED,RM_UAC_CREATED,FULFILMENT_REQUESTED,SAMPLE_LOADED                     |                        |
      | CE        | E             | Cont     | False     | False   | NONE        | sample_1_english_CE_estab.csv           | E       | RESPONSE_RECEIVED,RM_UAC_CREATED,PRINT_CASE_SELECTED,FULFILMENT_REQUESTED,SAMPLE_LOADED |                        |
      | CE        | U             | HH       | True      | AR < E  | UPDATE      | sample_1_english_CE_unit_expected_2.csv | E       | RESPONSE_RECEIVED,QUESTIONNAIRE_LINKED,UAC_UPDATED,SAMPLE_LOADED                        |                        |
      | CE        | U             | HH       | True      | AR = E  | CANCEL      | sample_1_english_CE_unit.csv            | E       | RESPONSE_RECEIVED,SAMPLE_LOADED,QUESTIONNAIRE_LINKED,UAC_UPDATED                        |                        |
      | CE        | U             | CE1      | False     | False   | NONE        | sample_1_english_CE_unit.csv            | E       | RESPONSE_RECEIVED,SAMPLE_LOADED,QUESTIONNAIRE_LINKED,UAC_UPDATED                        |                        |
      | CE        | U             | Cont     | False     | False   | NONE        | sample_1_english_CE_unit.csv            | E       | RESPONSE_RECEIVED,RM_UAC_CREATED,PRINT_CASE_SELECTED,FULFILMENT_REQUESTED,SAMPLE_LOADED |                        |
      | SPG       | E             | CE1      | False     | False   | NONE        | sample_1_ni_SPG_estab.csv               | N       | RESPONSE_RECEIVED,SAMPLE_LOADED,QUESTIONNAIRE_LINKED,UAC_UPDATED                        |                        |
      | SPG       | U             | HH       | False     | True    | CANCEL      | sample_1_english_SPG_unit.csv           | E       | SAMPLE_LOADED,RESPONSE_RECEIVED                                                         |                        |
      | SPG       | U             | CE1      | False     | False   | NONE        | sample_1_english_SPG_unit.csv           | E       | RESPONSE_RECEIVED,SAMPLE_LOADED,QUESTIONNAIRE_LINKED,UAC_UPDATED                        |                        |
      | SPG       | U             | Cont     | False     | False   | NONE        | sample_1_english_SPG_unit.csv           | E       | RESPONSE_RECEIVED,RM_UAC_CREATED,PRINT_CASE_SELECTED,FULFILMENT_REQUESTED,SAMPLE_LOADED |                        |


  Scenario Outline: CE U Receipted Cases output nothing to Field when AR > ER
    Given sample file "<sample file>" is loaded successfully
    And if required, a new qid and case are created for case type "<case type>" address level "<address level>" qid type "<qid type>" and country "<country>"
    When the receipt msg is put on the GCP pubsub
    And a uac_updated msg is emitted with active set to false for the receipted qid
    And a case_updated msg is emitted where "receiptReceived" is "True"
    And a CANCEL action instruction is sent to field work management with address type "CE"
    And a new qid and case are created for case type "CE" address level "U" qid type "<qid type>" and country "E"
    And the receipt msg is put on the GCP pubsub
    And a uac_updated msg is emitted with active set to false for the receipted qid
    Then the correct events are logged for loaded case events "[<loaded case events>]" and individual case events "[<individual case events>]"
    And if the actual response count is incremented "<increment>" or the case is marked receipted "<receipt>" then there should be a case updated message of case type "<case type>"
    And if the field instruction "<instruction>" is not NONE a msg to field is emitted

    Examples:
      | case type | address level | qid type | increment | receipt | instruction | sample file                  | country | loaded case events                                                                                                        | individual case events |
      | CE        | U             | Ind      | True      | AR > E  | NONE        | sample_1_english_CE_unit.csv | E       | RESPONSE_RECEIVED,RM_UAC_CREATED,FULFILMENT_REQUESTED,SAMPLE_LOADED,RESPONSE_RECEIVED,RM_UAC_CREATED,FULFILMENT_REQUESTED |                        |
      | CE        | U             | HH       | True      | AR > E  | NONE        | sample_1_english_CE_unit.csv | E       | RESPONSE_RECEIVED,QUESTIONNAIRE_LINKED,UAC_UPDATED,SAMPLE_LOADED,RESPONSE_RECEIVED,QUESTIONNAIRE_LINKED,UAC_UPDATED       |                        |


  Scenario: Receipted Cases are excluded from print files
    Given sample file "sample_input_england_census_spec.csv" is loaded successfully
    When the receipt msg for the created case is put on the GCP pubsub
    And we schedule an action rule of type "ICL1E" when case event "RESPONSE_RECEIVED" is logged
    Then only unreceipted cases appear in "P_IC_ICL1" print files
    And the events logged for the receipted case are [SAMPLE_LOADED,RESPONSE_RECEIVED]

  Scenario: Receipt of unaddressed continuation questionnaire does not send to Field
    Given sample file "sample_1_english_HH_unit.csv" is loaded successfully
    And an unaddressed QID request message of questionnaire type 11 is sent
    And a UACUpdated message not linked to a case is emitted to RH and Action Scheduler
    And a Questionnaire Linked message is sent
    When the offline receipt msg for a continuation form from the case is received
    Then no ActionInstruction is sent to FWMT

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
    And the receipt msg is put on the GCP pubsub and a uac_updated msg is emitted
    And an "UPDATE" field instruction is emitted
    And a case_updated msg is emitted where "receiptReceived" is "True"
    And a new qid and case are created for case type "CE" address level "E" qid type "Ind" and country "E"
    When the receipt msg is put on the GCP pubsub
    Then an "UPDATE" field instruction is emitted
    And if the actual response count is incremented "True" or the case is marked receipted "True" then there should be a case updated message of case type "CE"


    # CCS
  Scenario: EQ receipt for HH CCS case default UAC results in UAC updated event sent to RH
    Given a CCS Property List event is sent and associated "HH" case is created and sent to FWMT
    When the receipt msg for the created CCS case is put on the GCP pubsub
    Then a uac_updated msg is emitted with active set to false
    And a case_updated msg is emitted where "receiptReceived" is "True"
    And a CANCEL action instruction is sent to field work management with address type "HH"
    And the events logged for the receipted case are [CCS_ADDRESS_LISTED,RESPONSE_RECEIVED]

  Scenario Outline: Paper/postback questionnaire receipts for HH U level CCS case receipts the case
    Given an unaddressed QID request message of questionnaire type <questionnaire type> is sent and an unlinked uac is emitted
    And a CCS Property List event is sent and associated "HH" case with address level "U" is created and sent to FWMT
    And a Questionnaire Linked message is sent for the CCS case
    And a UAC updated event is emitted linking the UAC and QID to the CCS case
    When the offline receipt msg for the unlinked is put on the GCP pubsub
    Then a uac_updated msg is emitted with active set to false
    And a case_updated msg is emitted where "receiptReceived" is "True"
    And a "CANCEL" field instruction is emitted for the CCS case
    And the events logged for the receipted case are [CCS_ADDRESS_LISTED,QUESTIONNAIRE_LINKED,UAC_UPDATED,RESPONSE_RECEIVED]

    Examples:
      | questionnaire type |
      | 71                 |
      | 51                 |

    @regression
    Examples:
      | questionnaire type |
      | 72                 |
      | 73                 |
      | 74                 |
      | 52                 |
      | 53                 |
      | 54                 |

  Scenario Outline: CE Manager Paper receipt for CE E level CCS case receipts the case
    Given an unaddressed QID request message of questionnaire type <questionnaire type> is sent and an unlinked uac is emitted
    And a CCS Property List event is sent and associated "CE" case with address level "E" is created and sent to FWMT
    And a Questionnaire Linked message is sent for the CCS case
    And a UAC updated event is emitted linking the UAC and QID to the CCS case
    When the offline receipt msg for the unlinked is put on the GCP pubsub
    Then a uac_updated msg is emitted with active set to false
    And a case_updated msg is emitted where "receiptReceived" is "True"
    And an "UPDATE" field instruction is emitted for the CCS case
    And the events logged for the receipted case are [CCS_ADDRESS_LISTED,QUESTIONNAIRE_LINKED,UAC_UPDATED,RESPONSE_RECEIVED]

    Examples:
      | questionnaire type |
      | 81                 |

    @regression
    Examples:
      | questionnaire type |
      | 82                 |
      | 83                 |
      | 84                 |

  Scenario Outline: CCS Continuation questionnaire receipts are logged but do not receipt the case
    Given an unaddressed QID request message of questionnaire type <questionnaire type> is sent and an unlinked uac is emitted
    And a CCS Property List event is sent and associated "<address type>" case with address level "<address level>" is created and sent to FWMT
    And a Questionnaire Linked message is sent for the CCS case
    And a UAC updated event is emitted linking the UAC and QID to the CCS case
    When the offline receipt msg for the unlinked is put on the GCP pubsub
    Then a uac_updated msg is emitted with active set to false
    And the CCS case is not marked as receipted
    And no ActionInstruction is sent to FWMT
    And the events logged for the receipted case are [CCS_ADDRESS_LISTED,QUESTIONNAIRE_LINKED,UAC_UPDATED,RESPONSE_RECEIVED]

    Examples:
      | questionnaire type | address type | address level |
      | 61                 | HH           | U             |

# TODO Uncomment these rows to include 62 once the bug is patched
    @regression
    Examples:
      | questionnaire type | address type | address level |
#      | 62                 | HH           | U             |
      | 63                 | HH           | U             |
      | 61                 | CE           | U             |
#      | 62                 | CE           | U             |
      | 63                 | CE           | U             |
      | 61                 | CE           | E             |
#      | 62                 | CE           | E             |
      | 63                 | CE           | E             |
