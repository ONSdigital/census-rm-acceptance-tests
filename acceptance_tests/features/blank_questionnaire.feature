Feature: Handling Blank Questionnaire Scenario

  Scenario Outline: Blank questionnaire for non-CE case types
    Given sample file "<sample file>" is loaded successfully
    And if required, a new qid and case are created for case type "<case type>" address level "<address level>" qid type "<qid type>" and country "<country>"
    And the offline receipt msg for the receipted case is put on the GCP pubsub and expected uac inactive msg is emitted
    And a case_updated msg of type "<case type>" and address level "<address level>" is emitted where "receiptReceived" is "True" and qid is "<another qid receipted>"
    And if the field instruction "<offline receipt instruction>" is not NONE a msg to field is emitted
    And if required for "<form type>", a new qid is created "<another qid receipted>"
    When the blank questionnaire msg for a case is put on the GCP pubsub
    Then a uac_updated msg is emitted with active set to false for the receipted qid
    And a case_updated msg of type "<case type>" and address level "<address level>" is emitted where "receiptReceived" is "False" and qid is "<another qid receipted>"
    And the correct events are logged for loaded case events "[<loaded case events>]" and individual case events "[<individual case events>]"
    And if the field instruction "<blank instruction>" is not NONE a msg to field is emitted

    @smoke
    Examples:
      | case type | address level | qid type | form type | sample file                  | loaded case events                                | blank instruction | another qid receipted | country | offline receipt instruction | individual case events |
      | HH        | U             | HH       | 01        | sample_1_english_HH_unit.csv | SAMPLE_LOADED,RESPONSE_RECEIVED,RESPONSE_RECEIVED | UPDATE            | False                 | E       | CANCEL                      |                        |

    @regression
    Examples:
      | case type | address level | qid type | form type | sample file                   | loaded case events                                                                 | blank instruction | another qid receipted | country | offline receipt instruction | individual case events                             |
      | HH        | U             | HH       | 01        | sample_1_english_HH_unit.csv  | SAMPLE_LOADED,RESPONSE_RECEIVED,RESPONSE_RECEIVED,QUESTIONNAIRE_LINKED,UAC_UPDATED | NONE              | True                  | E       | CANCEL                      |                                                    |
      | SPG       | U             | HH       | 01        | sample_1_english_SPG_unit.csv | SAMPLE_LOADED,RESPONSE_RECEIVED,RESPONSE_RECEIVED                                  | UPDATE            | False                 | E       | CANCEL                      |                                                    |
      | SPG       | U             | HH       | 01        | sample_1_english_SPG_unit.csv | SAMPLE_LOADED,RESPONSE_RECEIVED,RESPONSE_RECEIVED,QUESTIONNAIRE_LINKED,UAC_UPDATED | NONE              | True                  | E       | CANCEL                      |                                                    |
      | HI        | U             | Ind      | 21        | sample_1_english_HH_unit.csv  | SAMPLE_LOADED,FULFILMENT_REQUESTED                                                 | NONE              | False                 | E       | NONE                        | RM_UAC_CREATED,RESPONSE_RECEIVED,RESPONSE_RECEIVED |


  Scenario Outline: Blank questionnaire for CE case types
    Given sample file "<sample file>" is loaded successfully
    And if required, a new qid and case are created for case type "<case type>" address level "<address level>" qid type "<qid type>" and country "<country>"
    And the offline receipt msg for the receipted case is put on the GCP pubsub and expected uac inactive msg is emitted
    And a case_updated msg of type "<case type>" and address level "<address level>" is emitted where "receiptReceived" is "True" and qid is "<another qid receipted>"
    And if the field instruction "<offline receipt instruction>" is not NONE a msg to field is emitted
    And if required for "<form type>", a new qid is created "<another qid receipted>"
    When the blank questionnaire msg for a case is put on the GCP pubsub
    Then a uac_updated msg is emitted with active set to false for the receipted qid
    And the correct events are logged for loaded case events "[<loaded case events>]" for blank questionnaire
    And if the field instruction "<blank instruction>" is not NONE a msg to field is emitted

    Examples:
      | case type | address level | qid type | form type | sample file                  | loaded case events                                                                    | blank instruction | another qid receipted | country | offline receipt instruction |
      | CE        | U             | Ind      | 21        | sample_1_english_CE_unit.csv | SAMPLE_LOADED,FULFILMENT_REQUESTED,RM_UAC_CREATED,RESPONSE_RECEIVED,RESPONSE_RECEIVED | NONE              | False                 | E       | CANCEL                      |

    @regression
    Examples:
      | case type | address level | qid type | form type | sample file                   | loaded case events                                                                                                     | blank instruction | another qid receipted | country | offline receipt instruction |
      | CE        | U             | Ind      | 21        | sample_1_english_CE_unit.csv  | SAMPLE_LOADED,FULFILMENT_REQUESTED,RM_UAC_CREATED,RESPONSE_RECEIVED,RESPONSE_RECEIVED,QUESTIONNAIRE_LINKED,UAC_UPDATED | NONE              | True                  | E       | CANCEL                      |
      | CE        | E             | Ind      | 21        | sample_1_english_CE_estab.csv | SAMPLE_LOADED,FULFILMENT_REQUESTED,RM_UAC_CREATED,RESPONSE_RECEIVED,RESPONSE_RECEIVED                                  | NONE              | False                 | E       | UPDATE                      |


  Scenario Outline: Blank questionnaire before actual receipt
    Given sample file "<sample file>" is loaded successfully
    And if required, a new qid and case are created for case type "<case type>" address level "<address level>" qid type "<qid type>" and country "<country>"
    And the blank questionnaire msg for a case is put on the GCP pubsub and expected uac inactive msg is emitted
    And a case_updated msg of type "<case type>" and address level "<address level>" is emitted where "receiptReceived" is "False" and qid is "<another qid receipted>"
    And if the field instruction "<instruction>" is not NONE a msg to field is emitted
    And if required for "<form type>", a new qid is created "<another qid receipted >"
    When the offline receipt msg for the receipted case is put on the GCP pubsub
    Then a uac_updated msg is emitted with active set to false for the receipted qid
    And a case_updated msg has not been emitted
    And the correct events are logged for loaded case events "[<loaded case events>]" and individual case events "[<individual case events>]"
    And the field instruction is "NONE"

    Examples:
      | case type | address level | qid type | form type | sample file                  | loaded case events                                | another qid receipted | country | instruction | individual case events |
      | HH        | U             | HH       | 01        | sample_1_english_HH_unit.csv | SAMPLE_LOADED,RESPONSE_RECEIVED,RESPONSE_RECEIVED | False                 | E       | UPDATE      |                        |

    @regression
    Examples:
      | case type | address level | qid type | form type | sample file                   | loaded case events                                | another qid receipted | country | instruction | individual case events                             |
      | SPG       | U             | HH       | 01        | sample_1_english_SPG_unit.csv | SAMPLE_LOADED,RESPONSE_RECEIVED,RESPONSE_RECEIVED | False                 | E       | UPDATE      |                                                    |
      | HI        | U             | Ind      | 21        | sample_1_english_HH_unit.csv  | SAMPLE_LOADED,FULFILMENT_REQUESTED                | False                 | E       | NONE        | RM_UAC_CREATED,RESPONSE_RECEIVED,RESPONSE_RECEIVED |


  Scenario Outline: Blank questionnaire for Individual qid types before actual receipt
    Given sample file "<sample file>" is loaded successfully
    And if required, a new qid and case are created for case type "<case type>" address level "<address level>" qid type "<qid type>" and country "<country>"
    And the blank questionnaire msg for a case is put on the GCP pubsub and expected uac inactive msg is emitted
    And if the field instruction "<instruction>" is not NONE a msg to field is emitted
    And if required for "<form type>", a new qid is created "<another qid receipted>"
    When the offline receipt msg for the receipted case is put on the GCP pubsub
    Then a uac_updated msg is emitted with active set to false for the receipted qid
    And the correct events are logged for loaded case events "[<loaded case events>]" for blank questionnaire
    And no ActionInstruction is sent to FWMT

    Examples:
      | case type | address level | qid type | form type | sample file                  | loaded case events                                                                    | another qid receipted | country | instruction |
      | CE        | U             | Ind      | 21        | sample_1_english_CE_unit.csv | SAMPLE_LOADED,FULFILMENT_REQUESTED,RM_UAC_CREATED,RESPONSE_RECEIVED,RESPONSE_RECEIVED | False                 | E       | NONE        |

    @regression
    Examples:
      | case type | address level | qid type | form type | sample file                   | loaded case events                                                                    | another qid receipted | country | instruction |
      | CE        | E             | Ind      | 21        | sample_1_english_CE_estab.csv | SAMPLE_LOADED,FULFILMENT_REQUESTED,RM_UAC_CREATED,RESPONSE_RECEIVED,RESPONSE_RECEIVED | False                 | E       | NONE        |

  Scenario Outline: Blank questionnaire for non-CE case types before actual receipt when another qid is needed
    Given sample file "<sample file>" is loaded successfully
    And if required, a new qid and case are created for case type "<case type>" address level "<address level>" qid type "<qid type>" and country "<country>"
    And the blank questionnaire msg for a case is put on the GCP pubsub and expected uac inactive msg is emitted
    And a case_updated msg of type "<case type>" and address level "<address level>" is emitted where "receiptReceived" is "False" and qid is "<another qid receipted>"
    And if the field instruction "<instruction>" is not NONE a msg to field is emitted
    And if required for "<form type>", a new qid is created "<another qid receipted>"
    When the offline receipt msg for the receipted case is put on the GCP pubsub
    Then a uac_updated msg is emitted with active set to false for the receipted qid
    And a case_updated msg of type "<case type>" and address level "<address level>" is emitted where "receiptReceived" is "True" and qid is "<another qid receipted>"
    And the correct events are logged for loaded case events "[<loaded case events>]" for blank questionnaire
    And if the field instruction "CANCEL" is not NONE a msg to field is emitted

    Examples:
      | case type | address level | qid type | form type | sample file                  | loaded case events                                                                 | another qid receipted | country | instruction |
      | HH        | U             | HH       | 01        | sample_1_english_HH_unit.csv | SAMPLE_LOADED,RESPONSE_RECEIVED,RESPONSE_RECEIVED,QUESTIONNAIRE_LINKED,UAC_UPDATED | True                  | E       | UPDATE      |

    @regression
    Examples:
      | case type | address level | qid type | form type | sample file                   | loaded case events                                                                 | another qid receipted | country | instruction |
      | SPG       | U             | HH       | 01        | sample_1_english_SPG_unit.csv | SAMPLE_LOADED,RESPONSE_RECEIVED,RESPONSE_RECEIVED,QUESTIONNAIRE_LINKED,UAC_UPDATED | True                  | E       | UPDATE      |


  Scenario: Blank questionnaire against an unlinked qid
    Given sample file "sample_1_english_HH_unit.csv" is loaded successfully
    And if required, a new qid and case are created for case type "HH" address level "U" qid type "HH" and country "E"
    And an unaddressed QID request message of questionnaire type 01 is sent and an UAC msg is emitted
    And the offline receipt msg for the unlinked is put on the GCP pubsub and the unlinked uac is emitted as inactive
    And a blank questionnaire receipts comes in for an unlinked qid and the correct uac msg is emitted
    When a Questionnaire Linked message is sent for blank questionnaire
    Then if the field instruction "UPDATE" is not NONE a msg to field is emitted


  Scenario: An eQ receipt still cancels follow up for a QID which has had a blank questionnaire returned
    Given sample file "sample_1_english_HH_unit.csv" is loaded successfully
    And the blank questionnaire msg for a case is put on the GCP pubsub and expected uac inactive msg is emitted
    And a case_updated msg is emitted where "receiptReceived" is "False"
    And an "UPDATE" field instruction is emitted
    When the eQ receipt msg is put on the GCP pubsub
    Then a uac_updated msg is emitted with active set to false
    And a case_updated msg is emitted where "receiptReceived" is "True"
    And a CANCEL action instruction is sent to field work management with address type "HH"
    And the events logged for the case are [SAMPLE_LOADED,RESPONSE_RECEIVED,RESPONSE_RECEIVED]

  Scenario: A blank questionnaire event received after an eQ receipt does not send the case for follow up
    Given sample file "sample_1_english_HH_unit.csv" is loaded successfully
    And the eQ receipt msg is put on the GCP pubsub
    And a case_updated msg is emitted where "receiptReceived" is "True"
    And a CANCEL action instruction is sent to field work management with address type "HH"
    When the blank questionnaire msg for a case is put on the GCP pubsub
    Then no ActionInstruction is sent to FWMT
    And the events logged for the case are [SAMPLE_LOADED,RESPONSE_RECEIVED,RESPONSE_RECEIVED]
