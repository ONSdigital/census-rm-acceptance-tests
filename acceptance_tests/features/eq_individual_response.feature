Feature: Request individual response via EQ

  Scenario Outline: Individual UAC SMS requests via EQ
    Given sample file "sample_1_english_HH_unit.csv" is loaded successfully
    When an individual SMS UAC fulfilment request "<fulfilment code>" message is sent by EQ
    Then a new individual child case for the fulfilment is emitted to RH and Action Scheduler
    And notify api was called with SMS template "<SMS template>"
    And a UAC updated message with "<questionnaire type>" questionnaire type is emitted for the individual case
    And the fulfilment request case has these events logged [SAMPLE_LOADED,FULFILMENT_REQUESTED]
    And the individual case has these events logged [RM_UAC_CREATED]

    Examples: Individual UAC fulfilment codes: <fulfilment code>
      | fulfilment code | questionnaire type | SMS template       |
      | UACIT1          | 21                 | individual English |

    @regression
    Examples: Individual UAC fulfilment codes: <fulfilment code>
      | fulfilment code | questionnaire type | SMS template                 |
      | UACIT2          | 22                 | individual Welsh and English |
      | UACIT2W         | 23                 | individual Welsh             |
      | UACIT4          | 24                 | individual Northern Ireland  |

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
