Feature: Handle fulfilment request events

  Scenario Outline: Household UAC SMS requests
    Given sample file "sample_1_english_HH_unit.csv" is loaded successfully
    When a UAC fulfilment request "<fulfilment code>" message for a created case is sent
    Then notify api was called with SMS template "<SMS template>"
    And a UAC updated message with "<questionnaire type>" questionnaire type is emitted
    And the fulfilment request case has these events logged [SAMPLE_LOADED,FULFILMENT_REQUESTED,RM_UAC_CREATED]

    @smoke
    Examples: Household UAC fulfilment codes: <fulfilment code>
      | fulfilment code | questionnaire type | SMS template      |
      | UACHHT1         | 01                 | household English |

    @regression
    Examples: Household UAC fulfilment codes: <fulfilment code>
      | fulfilment code | questionnaire type | SMS template                |
      | UACHHT2         | 02                 | household Welsh and English |
      | UACHHT2W        | 03                 | household Welsh             |
      | UACHHT4         | 04                 | household Northern Ireland  |

  Scenario Outline: Individual UAC SMS requests
    Given sample file "sample_1_english_HH_unit.csv" is loaded successfully
    When a UAC fulfilment request "<fulfilment code>" message for a created case is sent
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

  Scenario Outline: Generate print files and log events for questionnaire fulfilment requests
    Given sample file "sample_1_english_HH_unit.csv" is loaded successfully
    When a PQ fulfilment request event with fulfilment code "<fulfilment code>" is received by RM
    Then a UAC updated message with "<questionnaire type>" questionnaire type is emitted
    And correctly formatted on request questionnaire print and manifest files for "<fulfilment code>" are created
    And the questionnaire fulfilment case has these events logged [SAMPLE_LOADED,FULFILMENT_REQUESTED,RM_UAC_CREATED,PRINT_CASE_SELECTED]

    @smoke
    Examples: Questionnaire: <fulfilment code>
      | fulfilment code | questionnaire type |
      | P_OR_H1         | 01                 |

    @regression
    Examples: Questionnaire: <fulfilment code>
      | fulfilment code | questionnaire type |
      | P_OR_H2         | 02                 |
      | P_OR_H2W        | 03                 |
      | P_OR_H4         | 04                 |

  Scenario Outline: Generate print files and log events for continuation questionnaire fulfilment requests
    Given sample file "sample_1_english_HH_unit.csv" is loaded successfully
    When a PQ continuation fulfilment request event with fulfilment code "<fulfilment code>" is received by RM
    Then a UAC updated message with "<questionnaire type>" questionnaire type is emitted
    And correctly formatted on request contn questionnaire print and manifest files for "<fulfilment code>" are created
    And the questionnaire fulfilment case has these events logged [SAMPLE_LOADED,FULFILMENT_REQUESTED,RM_UAC_CREATED,PRINT_CASE_SELECTED]

    Examples: Continuation Questionnaires: <fulfilment code>
      | fulfilment code | questionnaire type |
      | P_OR_HC1        | 11                 |

    @regression
    Examples: Continuation Questionnaires: <fulfilment code>
      | fulfilment code | questionnaire type |
      | P_OR_HC2        | 12                 |
      | P_OR_HC2W       | 13                 |
      | P_OR_HC4        | 14                 |


  Scenario Outline: Generate print files and log events for Household UAC print fulfilment letter requests
    Given sample file "sample_1_english_HH_unit.csv" is loaded successfully
    When a HH print UAC fulfilment request "<fulfilment code>" message for a created case is sent
    Then a UAC updated message with "<questionnaire type>" questionnaire type is emitted
    And correctly formatted on request HH UAC supplementary material print and manifest files for "<fulfilment code>" are created
    And the fulfilment request event is logged

    Examples: UAC Questionnaires: <fulfilment code>
      | fulfilment code | questionnaire type |
      | P_UAC_UACHHP1   | 01                 |

    @regression
    Examples: UAC Questionnaires: <fulfilment code>
      | fulfilment code | questionnaire type |
      | P_UAC_UACHHP2B  | 02                 |
      | P_UAC_UACHHP4   | 04                 |


  Scenario Outline: Generate print files and log events for supplementary printed material fulfilment requests
    Given sample file "sample_1_english_HH_unit.csv" is loaded
    When a supplementary materials fulfilment request event with fulfilment code "<fulfilment code>" is received by RM
    Then correctly formatted on request supplementary material print and manifest files for "<fulfilment code>" are created
    And the fulfilment request event is logged

    @smoke
    Examples: Translation Booklet: <fulfilment code>
      | fulfilment code |
      | P_TB_TBARA1     |

    Examples: Large print questionnaire: <fulfilment code>
      | fulfilment code |
      | P_LP_HL1        |

    @regression
    Examples: Large print questionnaire: <fulfilment code>
      | fulfilment code |
      | P_LP_HL2W       |
      | P_LP_HL4        |

    @regression
    Examples: Translation Booklet: <fulfilment code>
      | fulfilment code |
      | P_TB_TBALB1     |
      | P_TB_TBAMH1     |
      | P_TB_TBARA2     |
      | P_TB_TBARA4     |
      | P_TB_TBARM1     |
      | P_TB_TBBEN1     |
      | P_TB_TBBEN2     |
      | P_TB_TBBOS1     |
      | P_TB_TBBUL1     |
      | P_TB_TBBUL2     |
      | P_TB_TBBUL4     |
      | P_TB_TBBUR1     |
      | P_TB_TBCAN1     |
      | P_TB_TBCAN2     |
      | P_TB_TBCAN4     |
      | P_TB_TBCZE1     |
      | P_TB_TBCZE4     |
      | P_TB_TBFAR1     |
      | P_TB_TBFAR2     |
      | P_TB_TBFRE1     |
      | P_TB_TBGER1     |
      | P_TB_TBGRE1     |
      | P_TB_TBGRE2     |
      | P_TB_TBGUJ1     |
      | P_TB_TBPAN1     |
      | P_TB_TBPAN2     |
      | P_TB_TBHEB1     |
      | P_TB_TBHIN1     |
      | P_TB_TBHUN1     |
      | P_TB_TBHUN4     |
      | P_TB_TBIRI4     |
      | P_TB_TBITA1     |
      | P_TB_TBITA2     |
      | P_TB_TBJAP1     |
      | P_TB_TBKOR1     |
      | P_TB_TBKUR1     |
      | P_TB_TBKUR2     |
      | P_TB_TBLAT1     |
      | P_TB_TBLAT2     |
      | P_TB_TBLAT4     |
      | P_TB_TBLIN1     |
      | P_TB_TBLIT1     |
      | P_TB_TBLIT4     |
      | P_TB_TBMAL1     |
      | P_TB_TBMAL2     |
      | P_TB_TBMAN1     |
      | P_TB_TBMAN2     |
      | P_TB_TBMAN4     |
      | P_TB_TBNEP1     |
      | P_TB_TBPAS1     |
      | P_TB_TBPAS2     |
      | P_TB_TBPOL1     |
      | P_TB_TBPOL2     |
      | P_TB_TBPOL4     |
      | P_TB_TBPOR1     |
      | P_TB_TBPOR2     |
      | P_TB_TBPOR4     |
      | P_TB_TBPOT1     |
      | P_TB_TBROM1     |
      | P_TB_TBROM4     |
      | P_TB_TBRUS1     |
      | P_TB_TBRUS2     |
      | P_TB_TBRUS4     |
      | P_TB_TBSLE1     |
      | P_TB_TBSLO1     |
      | P_TB_TBSLO4     |
      | P_TB_TBSOM1     |
      | P_TB_TBSOM4     |
      | P_TB_TBSPA1     |
      | P_TB_TBSPA2     |
      | P_TB_TBSWA1     |
      | P_TB_TBSWA2     |
      | P_TB_TBTAG1     |
      | P_TB_TBTAM1     |
      | P_TB_TBTHA1     |
      | P_TB_TBTHA2     |
      | P_TB_TBTET4     |
      | P_TB_TBTIG1     |
      | P_TB_TBTUR1     |
      | P_TB_TBUKR1     |
      | P_TB_TBULS4     |
      | P_TB_TBURD1     |
      | P_TB_TBVIE1     |
      | P_TB_TBYSH1     |

    Examples: Information leaflet: <fulfilment code>
      | fulfilment code |
      | P_ER_ILER1      |

    @regression
    Examples: Information leaflet: <fulfilment code>
      | fulfilment code |
      | P_ER_ILER2B     |

  Scenario Outline: Generate print files and log events for individual questionnaire fulfilment requests
    Given sample file "sample_1_english_HH_unit.csv" is loaded successfully
    When an individual print fulfilment request "<fulfilment code>" is received by RM
    Then a new individual child case for the fulfilment is emitted to RH and Action Scheduler
    And correctly formatted individual response questionnaires are created for "<fulfilment code>" with questionnaire type "<questionnaire type>"
    And the fulfilment request event is logged

    Examples: Individual Response Questionnaires fulfilment codes: <fulfilment code>
      | fulfilment code | questionnaire type |
      | P_OR_I1         | 21                 |

    @regression
    Examples: Individual Response Questionnaires fulfilment codes: <fulfilment code>
      | fulfilment code | questionnaire type |
      | P_OR_I2         | 22                 |
      | P_OR_I2W        | 23                 |
      | P_OR_I4         | 24                 |


  Scenario Outline: Generate print files and log events for individual UAC print fulfilment letter requests
    Given sample file "sample_1_english_HH_unit.csv" is loaded successfully
    When an individual print fulfilment request "<fulfilment code>" is received by RM
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

  Scenario: Generate individual cases and check that no actions rules are triggered for them
    Given sample file "sample_individual_case_spec.csv" is loaded successfully
    When a UAC fulfilment request "UACIT1" message for a created case is sent
    And set action rule of type "FIELD" when case event "FULFILMENT_REQUESTED" is logged
    Then the action instruction messages for only the HH case are emitted to FWMT where the case has a "treatmentCode" of "HH_QF2R1E"
    And an individual case has been created and only has logged events of [RM_UAC_CREATED]


  Scenario Outline: Generate print file and log events for two questionnaire fulfilment requests
    Given sample file "sample_2_english_units.csv" is loaded successfully
    When two PQ fulfilment request events with fulfilment code "<fulfilment code>" are received by RM
    Then two UAC updated messages with "<questionnaire type>" questionnaire type are emitted
    And correctly formatted on request fulfilment questionnaire print and manifest files for "<fulfilment code>" are created
    And the multiple questionnaire fulfilment cases have these events logged [SAMPLE_LOADED,FULFILMENT_REQUESTED,RM_UAC_CREATED,PRINT_CASE_SELECTED]

    Examples: Questionnaire: <fulfilment code>
      | fulfilment code | questionnaire type |
      | P_OR_H1         | 01                 |

  Scenario: Fulfilment is confirmed by QM
    Given sample file "sample_1_english_HH_unit.csv" is loaded successfully
    When QM sends a fulfilment confirmed message via pubsub
    Then the questionnaire fulfilment case has these events logged [SAMPLE_LOADED,FULFILMENT_CONFIRMED]

  Scenario: Fulfilment is confirmed by PPO
    Given sample file "sample_1_english_HH_unit.csv" is loaded successfully
    When PPO sends a fulfilment confirmed message via pubsub
    Then the questionnaire fulfilment case has these events logged [SAMPLE_LOADED,FULFILMENT_CONFIRMED]
