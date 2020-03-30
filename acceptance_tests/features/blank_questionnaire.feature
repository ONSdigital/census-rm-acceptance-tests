Feature: Handling Blank Questionnaire Scenario

Scenario Outline: Blank questionnairee for non CE case types
    Given sample file "<sample file>" is loaded successfully
    And if required a new qid and case are created for case type "<case type>" address level "<address level>" qid type "<qid type>" and country "<country>"
    And the offline receipt msg for the receipted case is put on the GCP pubsub
    And a uac_updated msg is emitted with active set to false for the receipted qid
    And a case_updated msg of type "<case type>" and address level "<address level>" is emitted where "receiptReceived" is "True" and qid is "<qid needed>"
    And if the field instruction "<instruction change>" is not NONE a msg to field is emitted
    And if required for "<form type>", a new qid is created "<qid needed>"
    When the blank questionnaire msg for a case is put on the GCP pubsub
    Then a uac_updated msg is emitted with active set to false for the receipted qid
    And a case_updated msg of type "<case type>" and address level "<address level>" is emitted where "receiptReceived" is "False" and qid is "<qid needed>"
    And the correct events are logged for loaded case events "[<loaded case events>]" and individual case events "[<individual case events>]"
    And if the field instruction "<instruction>" is not NONE a msg to field is emitted

    Examples:
      | case type | address level | qid type | form type | sample file                   | loaded case events                                               | instruction | qid needed | country | instruction change | individual case events                             |
      | HH        | U             | HH       | 01        | sample_1_english_HH_unit.csv  | SAMPLE_LOADED,RESPONSE_RECEIVED,RESPONSE_RECEIVED                | UPDATE      | False      | E       | CLOSE              |                                                    |
      | HH        | U             | HH       | 01        | sample_1_english_HH_unit.csv  | SAMPLE_LOADED,RM_UAC_CREATED,RESPONSE_RECEIVED,RESPONSE_RECEIVED | NONE        | True       | E       | CLOSE              |                                                    |
      | SPG       | U             | HH       | 01        | sample_1_english_SPG_unit.csv | SAMPLE_LOADED,RESPONSE_RECEIVED,RESPONSE_RECEIVED                | UPDATE      | False      | E       | CLOSE              |                                                    |
      | SPG       | U             | HH       | 01        | sample_1_english_SPG_unit.csv | SAMPLE_LOADED,RM_UAC_CREATED,RESPONSE_RECEIVED,RESPONSE_RECEIVED | NONE        | True       | E       | CLOSE              |                                                    |
      | HI        | U             | Ind      | 21        | sample_1_english_HH_unit.csv  | SAMPLE_LOADED,FULFILMENT_REQUESTED                               | NONE        | False      | E       | NONE               | RM_UAC_CREATED,RESPONSE_RECEIVED,RESPONSE_RECEIVED |


  Scenario Outline: Blank questionnaire for CE case types
    Given sample file "<sample file>" is loaded successfully
    And if required a new qid and case are created for case type "<case type>" address level "<address level>" qid type "<qid type>" and country "<country>"
    And the offline receipt msg for the receipted case is put on the GCP pubsub
    And a uac_updated msg is emitted with active set to false for the receipted qid
    And a case_updated msg of type "<case type>" and address level "<address level>" is emitted where "receiptReceived" is "True" and qid is "<qid needed>"
    And if the field instruction "<instruction change>" is not NONE a msg to field is emitted
    And if required for "<form type>", a new qid is created "<qid needed>"
    When the blank questionnaire msg for a case is put on the GCP pubsub
    Then a uac_updated msg is emitted with active set to false for the receipted qid
    And the correct events are logged for loaded case events "[<loaded case events>]" for blank questionnaire
    And if the field instruction "<instruction>" is not NONE a msg to field is emitted

    Examples:
      | case type | address level | qid type | form type | sample file                   | loaded case events                                                                                   | instruction | qid needed | country | instruction change |
      | CE        | U             | Ind      | 21        | sample_1_english_CE_unit.csv  | SAMPLE_LOADED,RM_UAC_CREATED,FULFILMENT_REQUESTED,RESPONSE_RECEIVED,RESPONSE_RECEIVED                | NONE        | False      | E       | CLOSE              |
      | CE        | U             | Ind      | 21        | sample_1_english_CE_unit.csv  | SAMPLE_LOADED,RM_UAC_CREATED,RM_UAC_CREATED,FULFILMENT_REQUESTED,RESPONSE_RECEIVED,RESPONSE_RECEIVED | NONE        | True       | E       | CLOSE              |
      | CE        | E             | Ind      | 21        | sample_1_english_CE_estab.csv | SAMPLE_LOADED,RM_UAC_CREATED,FULFILMENT_REQUESTED,RESPONSE_RECEIVED,RESPONSE_RECEIVED                | NONE        | False      | E       | UPDATE             |


  Scenario Outline: Blank questionnaire before actual receipt
    Given sample file "<sample file>" is loaded successfully
    And if required a new qid and case are created for case type "<case type>" address level "<address level>" qid type "<qid type>" and country "<country>"
    And the blank questionnaire msg for a case is put on the GCP pubsub
    And a uac_updated msg is emitted with active set to false for the receipted qid
    And a case_updated msg of type "<case type>" and address level "<address level>" is emitted where "receiptReceived" is "False" and qid is "<qid needed>"
    And if the field instruction "<instruction>" is not NONE a msg to field is emitted
    And if required for "<form type>", a new qid is created "<qid needed>"
    When the offline receipt msg for the receipted case is put on the GCP pubsub
    Then a uac_updated msg is emitted with active set to false for the receipted qid
    And a case_updated msg has not been emitted
    And the correct events are logged for loaded case events "[<loaded case events>]" and individual case events "[<individual case events>]"
    And the field instruction is "NONE"

    Examples:
      | case type | address level | qid type | form type | sample file                   | loaded case events                                | qid needed | country | instruction | individual case events                             |
      | HH        | U             | HH       | 01        | sample_1_english_HH_unit.csv  | SAMPLE_LOADED,RESPONSE_RECEIVED,RESPONSE_RECEIVED | False      | E       | UPDATE      |                                                    |
      | SPG       | U             | HH       | 01        | sample_1_english_SPG_unit.csv | SAMPLE_LOADED,RESPONSE_RECEIVED,RESPONSE_RECEIVED | False      | E       | UPDATE      |                                                    |
      | HI        | U             | Ind      | 21        | sample_1_english_HH_unit.csv  | SAMPLE_LOADED,FULFILMENT_REQUESTED                | False      | E       | NONE        | RM_UAC_CREATED,RESPONSE_RECEIVED,RESPONSE_RECEIVED |


  Scenario Outline: Blank questionnaire for Individual qid types before actual receipt
    Given sample file "<sample file>" is loaded successfully
    And if required a new qid and case are created for case type "<case type>" address level "<address level>" qid type "<qid type>" and country "<country>"
    And the blank questionnaire msg for a case is put on the GCP pubsub
    And a uac_updated msg is emitted with active set to false for the receipted qid
    And if the field instruction "<instruction>" is not NONE a msg to field is emitted
    And if required for "<form type>", a new qid is created "<qid needed>"
    When the offline receipt msg for the receipted case is put on the GCP pubsub
    Then a uac_updated msg is emitted with active set to false for the receipted qid
    And the correct events are logged for loaded case events "[<loaded case events>]" for blank questionnaire
    And the field instruction is "NONE"

    Examples:
      | case type | address level | qid type | form type | sample file                   | loaded case events                                                                    | qid needed | country | instruction |
      | CE        | U             | Ind      | 21        | sample_1_english_CE_unit.csv  | SAMPLE_LOADED,RM_UAC_CREATED,FULFILMENT_REQUESTED,RESPONSE_RECEIVED,RESPONSE_RECEIVED | False      | E       | NONE        |
      | CE        | E             | Ind      | 21        | sample_1_english_CE_estab.csv | SAMPLE_LOADED,RM_UAC_CREATED,FULFILMENT_REQUESTED,RESPONSE_RECEIVED,RESPONSE_RECEIVED | False      | E       | NONE        |
      | HH        | U             | HH       | 01        | sample_1_english_HH_unit.csv  | SAMPLE_LOADED,RM_UAC_CREATED,RESPONSE_RECEIVED,RESPONSE_RECEIVED                      | True       | E       | UPDATE      |

  Scenario Outline: Blank questionnaire for non-ce types before actual receipt and another qid needed
    Given sample file "<sample file>" is loaded successfully
    And if required a new qid and case are created for case type "<case type>" address level "<address level>" qid type "<qid type>" and country "<country>"
    And the blank questionnaire msg for a case is put on the GCP pubsub
    And a uac_updated msg is emitted with active set to false for the receipted qid
    And a case_updated msg of type "<case type>" and address level "<address level>" is emitted where "receiptReceived" is "False" and qid is "<qid needed>"
    And if the field instruction "<instruction>" is not NONE a msg to field is emitted
    And if required for "<form type>", a new qid is created "<qid needed>"
    When the offline receipt msg for the receipted case is put on the GCP pubsub
    Then a uac_updated msg is emitted with active set to false for the receipted qid
    And a case_updated msg of type "<case type>" and address level "<address level>" is emitted where "receiptReceived" is "True" and qid is "<qid needed>"
    And the correct events are logged for loaded case events "[<loaded case events>]" for blank questionnaire
    And if the field instruction "CLOSE" is not NONE a msg to field is emitted

    Examples:
      | case type | address level | qid type | form type | sample file                   | loaded case events                                               | qid needed | country | instruction |
      | HH        | U             | HH       | 01        | sample_1_english_HH_unit.csv  | SAMPLE_LOADED,RM_UAC_CREATED,RESPONSE_RECEIVED,RESPONSE_RECEIVED | True       | E       | UPDATE      |
      | SPG       | U             | HH       | 01        | sample_1_english_SPG_unit.csv | SAMPLE_LOADED,RM_UAC_CREATED,RESPONSE_RECEIVED,RESPONSE_RECEIVED | True       | E       | UPDATE      |

