Feature: QID's can be linked to cases

  @regression
  Scenario Outline: Any non-individual QID can be linked to any case type and address level
    Given sample file "<sample file>" is loaded successfully
    And unaddressed QID request messages for every non-individual type census type are sent and an unlinked uacs are emitted
    When a Questionnaire Linked message is sent for every requested qid
    Then a UAC updated event is emitted for every QID linking them to the case

    Examples:
      | sample file                   |
      | sample_1_english_HH_unit.csv  |
      | sample_1_english_CE_estab.csv |
      | sample_1_english_CE_unit.csv  |
      | sample_1_welsh_SPG_estab.csv  |
      | sample_1_english_SPG_unit.csv |

  @regression
  Scenario Outline: Any individual QID can be linked to any non HH case type and address level
    Given sample file "<sample file>" is loaded successfully
    And unaddressed QID request messages for every individual type census type are sent and an unlinked uacs are emitted
    When a Questionnaire Linked message is sent for every requested qid
    Then a UAC updated event is emitted for every QID linking them to the case

    Examples:
      | sample file                   |
      | sample_1_english_CE_estab.csv |
      | sample_1_english_CE_unit.csv  |
      | sample_1_welsh_SPG_estab.csv  |
      | sample_1_english_SPG_unit.csv |

  Scenario Outline: Any individual QID can be linked to a HH case, creating a HI case
    Given sample file "sample_1_english_HH_unit.csv" is loaded successfully
    When an unaddressed QID request message of questionnaire type <questionnaire type> is sent
    And a UACUpdated message not linked to a case is emitted to RH and Action Scheduler
    And an Individual Questionnaire Linked message is sent and ingested
    Then a Questionnaire Linked event is logged
    And the HI individual case can be retrieved

    Examples:
      | questionnaire type |
      | 21                 |

    @regression
    Examples:
      | questionnaire type |
      | 22                 |
      | 23                 |
      | 24                 |

  Scenario: Questionnaire linked to unaddressed
    Given sample file "sample_for_questionnaire_linked.csv" is loaded successfully
    When an unaddressed QID request message of questionnaire type 01 is sent
    And a UACUpdated message not linked to a case is emitted to RH and Action Scheduler
    And a Questionnaire Linked message is sent
    Then a Questionnaire Linked event is logged

  Scenario: Questionnaire linked to unaddressed CCS case
    Given a CCS Property List event is sent and associated "HH" case is created and sent to FWMT
    When an unaddressed QID request message of questionnaire type 01 is sent
    And a UACUpdated message not linked to a case is emitted to RH and Action Scheduler
    And a Questionnaire Linked message is sent for the CCS case
    Then a Questionnaire Linked event is logged

  Scenario: Individual Questionnaire linked to unaddressed without specifying individual case ID
    Given sample file "sample_for_questionnaire_linked.csv" is loaded successfully
    When an unaddressed QID request message of questionnaire type 21 is sent
    And a UACUpdated message not linked to a case is emitted to RH and Action Scheduler
    And an Individual Questionnaire Linked message with no individual case ID is sent and ingested
    Then a Questionnaire Linked event is logged
    And the HI individual case can be retrieved

  Scenario: A Questionnaire linked event ignores the IndividualCaseId if linking to a CE case
    Given sample file "sample_3_welsh_CE_estab.csv" is loaded successfully
    When an unaddressed QID request message of questionnaire type 21 is sent
    And a UACUpdated message not linked to a case is emitted to RH and Action Scheduler
    And an Individual Questionnaire Linked message is sent and ingested
    Then a Questionnaire Linked event on the parent case is logged

  Scenario: Receipt of unlinked unaddressed
    Given an unaddressed QID request message of questionnaire type 01 is sent
    And a UACUpdated message not linked to a case is emitted to RH and Action Scheduler
    When a receipt for the unlinked UAC-QID pair is received
    Then message redelivery does not go bananas

  Scenario: Unlinked QID is relinked to new case
    Given sample file "sample_for_questionnaire_linked.csv" is loaded successfully
    When an unaddressed QID request message of questionnaire type 01 is sent
    And a UACUpdated message not linked to a case is emitted to RH and Action Scheduler
    And a Questionnaire Linked message is sent
    And a Questionnaire Linked event is logged
    And a Questionnaire Linked message is sent to relink to a new case
    Then a Questionnaire Linked event is logged
    And a Questionnaire Unlinked event is logged
