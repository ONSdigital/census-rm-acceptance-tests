Feature: Handle fulfilment request events

  Scenario: Log event when a fulfilment request event is received
    Given sample file "sample_input_england_census_spec.csv" is loaded
    And messages are emitted to RH and Action Scheduler with [01] questionnaire types
    When a UAC fulfilment request "UACHHT1" message for a created case is sent
    And notify api was called with template id "21447bc2-e7c7-41ba-8c5e-7a5893068525"
    And the fulfilment request case has these events logged [SAMPLE_LOADED,FULFILMENT_REQUESTED,RM_UAC_CREATED]

  Scenario: Individual Response Fulfilment is received Log event without contact details, save new case, emit new case
    Given sample file "sample_input_england_census_spec.csv" is loaded
    And messages are emitted to RH and Action Scheduler with [01] questionnaire types
    When a UAC fulfilment request "UACIT1" message for a created case is sent
    Then a new child case is emitted to RH and Action Scheduler
    And notify api was called with template id "1ccd02a4-9b90-4234-ab7a-9215cb498f14"
    And the fulfilment request case has these events logged [SAMPLE_LOADED,FULFILMENT_REQUESTED]
    And the individual case has these events logged [RM_UAC_CREATED]

  Scenario Outline: Generate print files and log events for questionnaire fulfilment requests
    Given sample file "sample_1_english_unit.csv" is loaded
    And messages are emitted to RH and Action Scheduler with [01] questionnaire types
    When a PQ fulfilment request event with fulfilment code "<fulfilment code>" is received by RM
    Then a UAC updated message with "<questionnaire type>" questionnaire type is emitted
    And correctly formatted on request questionnaire print and manifest files for "<fulfilment code>" are created
    And the questionnaire fulfilment case has these events logged [SAMPLE_LOADED,FULFILMENT_REQUESTED,RM_UAC_CREATED]

    Examples: Questionnaire: <fulfilment code>
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
    And the questionnaire fulfilment case has these events logged [SAMPLE_LOADED,FULFILMENT_REQUESTED,RM_UAC_CREATED]

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

    Examples: Large print questionnaire: <fulfilment code>
      | fulfilment code |
      | P_LP_HL1        |
      | P_LP_HL2W       |
      | P_LP_HL4        |

    Examples: Translation Booklet: <fulfilment code>
      | fulfilment code |
      | P_TB_TBARA1     |
      | P_TB_TBPOL4     |
      | P_TB_TBYSH1     |


<<<<<<< HEAD
  Scenario Outline: Generate print files and log events for individual questionnaire fulfilment requests
    Given sample file "sample_1_english_unit.csv" is loaded
    And messages are emitted to RH and Action Scheduler with [01] questionnaire types
    When an individual print fulfilment request "<fulfilment code>" is received by RM
    Then a new child case is emitted to RH and Action Scheduler
    And correctly formatted individual response questionnaires are are created with "<fulfilment code>"
    And the fulfilment request event is logged

    Examples: Individual Response Questionnaires fulfilment codes
      | fulfilment code |
      | P_OR_I1         |
      | P_OR_I2         |
      | P_OR_I2W        |
      | P_OR_I4         |


    
  Scenario: Generate individual cases and check that no actions rules are triggered for them
    Given sample file "sample_individual_case_spec.csv" is loaded successfully
    And an action rule of type "FF2QE" is set 10 seconds in the future
    When a UAC fulfilment request "UACIT1" message for a created case is sent
    Then the action instruction messages are emitted to FWMT where the case has a treatment code of "HH_QF2R1E"


