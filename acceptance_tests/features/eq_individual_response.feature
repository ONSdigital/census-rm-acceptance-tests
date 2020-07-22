Feature: Request individual response via EQ

  Scenario Outline: Individual UAC SMS requests via EQ
    Given sample file "sample_1_english_HH_unit.csv" is loaded successfully
    When an individual SMS UAC fulfilment request "<fulfilment code>" message is sent by EQ
    Then a new individual child case for the fulfilment is emitted to RH and Action Scheduler
    And notify api was called with SMS template for fulfilment code "<fulfilment code>"
    And a UAC updated message with "<questionnaire type>" questionnaire type is emitted for the individual case
    And the fulfilment request case has these events logged [SAMPLE_LOADED,FULFILMENT_REQUESTED]
    And the individual case has these events logged [RM_UAC_CREATED]

    Examples: Individual UAC fulfilment codes: <fulfilment code>
      | fulfilment code | questionnaire type |
      | UACIT1          | 21                 |

    @regression
    Examples: Individual UAC fulfilment codes: <fulfilment code>
      | fulfilment code | questionnaire type |
      | UACIT2          | 22                 |
      | UACIT2W         | 23                 |
      | UACIT4          | 24                 |

  Scenario Outline: Individual UAC print requests via EQ
    Given sample file "sample_1_english_HH_unit.csv" is loaded successfully
    When an individual print UAC fulfilment request "<fulfilment code>" message is sent by EQ
    Then a new individual child case for the fulfilment is emitted to RH and Action Scheduler
    And correctly formatted individual UAC print responses are created for "<fulfilment code>" with questionnaire type "<questionnaire type>"
    And the fulfilment request event is logged

    Examples: Individual UAC Response fulfilment codes: <fulfilment code>
      | fulfilment code | questionnaire type |
      | P_UAC_UACIP1    | 21                 |

    @regression
    Examples: Individual UAC Response fulfilment codes: <fulfilment code>
      | fulfilment code | questionnaire type |
      | P_UAC_UACIP2B   | 22                 |
      | P_UAC_UACIP4    | 24                 |
