Feature: Case processor handles receipt message from pubsub service
  Case LogEvent set on our system

  Scenario: eQ receipt results in UAC updated event sent to RH
    Given sample file "sample_for_receipting.csv" is loaded
    And messages are emitted to RH and Action Scheduler with [01] questionnaire types
    When the receipt msg for the created case is put on the GCP pubsub
    Then a uac_updated msg is emitted with active set to false
    And a case_updated msg is emitted where "receiptReceived" is "True"
    And an ActionCancelled event is sent to field work management
    And the events logged for the receipted case are [SAMPLE_LOADED,RESPONSE_RECEIVED]

  Scenario: eQ receipt results in UAC updated event sent to RH, simulate missing case_id
    Given sample file "sample_for_receipting.csv" is loaded
    And messages are emitted to RH and Action Scheduler with [01] questionnaire types
    When the receipt msg for the created case is put on the GCP pubsub with just qid
    Then a uac_updated msg is emitted with active set to false
    And a case_updated msg is emitted where "receiptReceived" is "True"
    And an ActionCancelled event is sent to field work management
    And the events logged for the receipted case are [RESPONSE_RECEIVED,SAMPLE_LOADED]

  Scenario: PQRS receipt results in UAC updated event sent to RH
    Given sample file "sample_for_receipting.csv" is loaded
    And messages are emitted to RH and Action Scheduler with [01] questionnaire types
    When the offline receipt msg for the created case is put on the GCP pubsub
    Then a uac_updated msg is emitted with active set to false
    And a case_updated msg is emitted where "receiptReceived" is "True"
    And an ActionCancelled event is sent to field work management
    And the events logged for the receipted case are [SAMPLE_LOADED,RESPONSE_RECEIVED]

  Scenario: Receipted Cases are excluded from print files
    Given an action rule of type "ICL1E" is set 10 seconds in the future
    And sample file "sample_input_england_census_spec.csv" is loaded
    And messages are emitted to RH and Action Scheduler with [01] questionnaire types
    When the receipt msg for a created case is put on the GCP pubsub
    Then only unreceipted cases appear in "P_IC_ICL1" print files
    And a case_updated msg is emitted where "receiptReceived" is "True"
    And the events logged for the receipted case are [SAMPLE_LOADED,RESPONSE_RECEIVED]


  Scenario Outline:  Generate print files and log events for response driven reminders
    Given sample file "<sample file>" is loaded successfully
    And an action rule of type "<pack code>" is set 2 seconds in the future
    When UAC Updated events emitted for the <number of matching cases> cases with matching treatment codes
    Then correctly formatted "<pack code>" reminder letter print files are created
    And there is a correct "<pack code>" manifest file for each csv file written
    And "PRINT_CASE_SELECTED" events are logged against the cases included in the reminder

    Examples: Reminder contact letter: <pack code>
      | pack code    | number of matching cases | sample file                                        |
      | P_RD_2RL1_1  | 3                        | sample_input_england_response_driven_reminders.csv |
      | P_RD_2RL2B_1 | 1                        | sample_input_wales_census_spec.csv                 |
      | P_RD_2RL1_2  | 2                        | sample_input_england_response_driven_reminders.csv |
      | P_RD_2RL2B_2 | 2                        | sample_input_wales_census_spec.csv                 |
      | P_RD_2RL1_3  | 1                        | sample_input_england_response_driven_reminders.csv |
      | P_RD_2RL2B_3 | 1                        | sample_input_wales_census_spec.csv