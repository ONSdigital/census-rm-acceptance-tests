Feature: Field follow-up filtering - Cases excluded from fieldwork

  Scenario: Given I have created a new case at sample load loaded the samples
    Given sample file "sample_1_input_nisra_census_spec.csv" is loaded successfully
    And an export file template has been created with template "P_IC_H1"
    When an export file action rule has been created for packcode "P_IC_H1"
    Then UAC_UPDATE message is emitted with active set to true
    When case events are sent to the fieldwork adapter
    Then a create message will not be generated for field
    And no fieldwork action instruction messages are sent for N region cases

  Scenario: Given I have updated a case
    Given sample file "sample_1_input_nisra_census_spec.csv" is loaded successfully
    And an export file template has been created with template "P_IC_H1"
    When an export file action rule has been created for packcode "P_IC_H1"
    Then UAC_UPDATE message is emitted with active set to true
    When case events are sent to the fieldwork adapter
    Then an update message will not be generated for field
    And no fieldwork action instruction messages are sent for N region cases
