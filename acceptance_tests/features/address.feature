Feature: Address updates

  Scenario Outline: Invalid address event for HH, CE and SPG case types for unit level cases
    Given sample file "<sample file>" is loaded successfully
    When an invalid address message is sent from "CC"
    Then a case_updated msg is emitted where "addressInvalid" is "True"
    And an ActionCancelled event is sent to field work management
    And the case event log records invalid address

    Examples:
      | sample file                             |
      | sample_for_questionnaire_linked.csv     |
      | sample_for_invalid_address_CE_U.csv     |
      | sample_for_invalid_address_SPG_U.csv    |