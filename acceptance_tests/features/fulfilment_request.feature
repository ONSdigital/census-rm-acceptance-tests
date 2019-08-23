Feature: Handle fulfilment request events

  Scenario: Log event when a fulfilment request event is received
    Given sample file "sample_input_england_census_spec.csv" is loaded
    And messages are emitted to RH and Action Scheduler with [01] questionnaire types
    When a UAC fulfilment request "UACHHT1" message for a created case is sent
    Then a fulfilment request event is logged
    And notify api was called with template id "21447bc2-e7c7-41ba-8c5e-7a5893068525"

  Scenario: Individual Response Fulfilment is received Log event without contact details, save new case, emit new case
    Given sample file "sample_input_england_census_spec.csv" is loaded
    And messages are emitted to RH and Action Scheduler with [01] questionnaire types
    When a UAC fulfilment request "UACIT1" message for a created case is sent
    Then a fulfilment request event is logged
    And a new child case is emitted to RH and Action Scheduler
    And notify api was called with template id "1ccd02a4-9b90-4234-ab7a-9215cb498f14"

  Scenario Outline: Generate print files and log events for questionnaire fulfilment requests
    Given sample file "sample_1_english_unit.csv" is loaded
    And messages are emitted to RH and Action Scheduler with [01] questionnaire types
    When a PQ fulfilment request event with fulfilment code "<fulfilment code>" is received by RM
    Then a UAC updated message with "<questionnaire type>" questionnaire type is emitted
    And correctly formatted on request questionnaire print and manifest files for "<fulfilment code>" are created
    And the fulfilment request event is logged

    Examples: Questionnaires
      | fulfilment code | questionnaire type |
      | P_OR_H1         | 01                 |
      | P_OR_H2         | 02                 |
      | P_OR_H2W        | 03                 |
      | P_OR_H4         | 04                 |

  Scenario Outline: Generate print files and log events for continuation questionnaire fulfilment requests
    Given sample file "sample_1_english_unit.csv" is loaded
    And messages are emitted to RH and Action Scheduler with [01] questionnaire types
    When a PQ continuation fulfilment request event with fulfilment code "<fulfilment code>" is received by RM
    Then a UAC updated message with "<questionnaire type>" questionnaire type is emitted
    And correctly formatted on request contn questionnaire print and manifest files for "<fulfilment code>" are created
    And the continuation fulfilment request event is logged

    Examples: Continuation Questionnaires
      | fulfilment code | questionnaire type |
      | P_OR_HC1        | 11                 |
      | P_OR_HC2        | 12                 |
      | P_OR_HC2W       | 13                 |
      | P_OR_HC4        | 14                 |

  Scenario Outline: Generate print files and log events for supplementary printed material fulfilment requests
    Given sample file "sample_1_english_unit.csv" is loaded
    When a supplementary materials fulfilment request event with fulfilment code "<fulfilment code>" is received by RM
    Then correctly formatted on request supplementary material print and manifest files for "<fulfilment code>" are created
    And the fulfilment request event is logged

    Examples: Large print questionnaires
      | fulfilment code |
      | P_LP_HL1        |
      | P_LP_HL2W       |
      | P_LP_HL4        |

    Examples: Translation Booklets
      | fulfilment code |
      | P_TB_TBARA1     |
      | P_TB_TBPOL4     |
      | P_TB_TBYSH1     |
