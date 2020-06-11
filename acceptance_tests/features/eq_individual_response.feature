Feature: Request individual response via EQ

  Scenario Outline: Individual UAC SMS requests via EQ
    Given sample file "sample_1_english_HH_unit.csv" is loaded successfully
    When an individual SMS UAC fulfilment request "<fulfilment code>" message is sent by EQ
    Then a new individual child case for the fulfilment is emitted to RH and Action Scheduler
    And notify api was called with template id "<template ID>"
    And a UAC updated message with "<questionnaire type>" questionnaire type is emitted for the individual case
    And the fulfilment request case has these events logged [SAMPLE_LOADED,FULFILMENT_REQUESTED]
    And the individual case has these events logged [RM_UAC_CREATED]

    Examples: Household UAC fulfilment codes: <fulfilment code>
      | fulfilment code | questionnaire type | template ID                          |
      | UACIT1          | 21                 | 21447bc2-e7c7-41ba-8c5e-7a5893068525 |

    @regression
    Examples: Household UAC fulfilment codes: <fulfilment code>
      | fulfilment code | questionnaire type | template ID                          |
      | UACIT2          | 22                 | 23f96daf-9674-4087-acfc-ffe98a52cf16 |
      # TODO UACIT2W should be type 23
      | UACIT2W         | 22                 | ef045f43-ffa8-4047-b8e2-65bfbce0f026 |
      | UACIT4          | 24                 | 1ccd02a4-9b90-4234-ab7a-9215cb498f14 |

  Scenario Outline: Individual UAC print requests via EQ
    Given sample file "sample_1_english_HH_unit.csv" is loaded successfully
    When an individual print UAC fulfilment request "<fulfilment code>" message is sent by EQ
    Then a new individual child case for the fulfilment is emitted to RH and Action Scheduler
    And correctly formatted individual response questionnaires are created for "<fulfilment code>" with questionnaire type "<questionnaire type>"
    And the fulfilment request event is logged

    Examples: Individual Response Questionnaires fulfilment codes
      | fulfilment code | questionnaire type |
      | P_OR_I1         | 21                 |

    @regression
    Examples: Individual Response Questionnaires fulfilment codes
      | fulfilment code | questionnaire type |
      | P_OR_I2         | 22                 |
      | P_OR_I2W        | 23                 |
      | P_OR_I4         | 24                 |
