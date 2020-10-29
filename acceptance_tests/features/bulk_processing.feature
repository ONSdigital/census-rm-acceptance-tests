@regression
Feature: Bulk event CSV files can be processed

  Scenario: A bulk refusal file is successfully ingested
    Given sample file "sample_input_wales_census_spec.csv" is loaded successfully
    And a bulk refusal file is supplied
    When the bulk refusal file is processed
    Then the cases are marked with the correct refusal

  Scenario: A bulk new address file is successfully ingested
    Given a bulk new address file "new_addresses_33.csv" is supplied
    When the bulk new address file is processed
    Then CASE_CREATED events are emitted for all the new addressed supplied
    And the new address cases are ingested into the database
    And the new address cases are sent to field as CREATE with UAA true

  Scenario: A bulk invalid address file is successfully ingested
    Given sample file "sample_input_wales_census_spec.csv" is loaded successfully
    And a bulk invalid address file is supplied
    When the bulk invalid address file is processed
    Then CASE_UPDATED events are emitted for all the cases in the file with addressInvalid true

  Scenario: A bulk deactivate uac file is successfully ingested
    Given sample file "sample_for_print_stories.csv" is loaded successfully
    And a bulk deactivate uac file is supplied
    When the bulk deactivate file is processed
    Then UAC_UPDATED msgs with active set to false for all the original uacs created
    And every created UAC QID pair has a DEACTIVATE_UAC event logged against it

  Scenario: A bulk address update file is successfully ingested
    Given sample file "HH_unit_and_NI_CE_unit.csv" is loaded successfully
    And a bulk address update file is supplied
    When the bulk address update file is processed
    Then CASE_UPDATED events are emitted for all the updated cases with correctly updated data and skeleton marker false
    And the cases are updated in the database
    And an UPDATE message is sent to field for each updated case excluding NI CE, "TRANSIENT PERSONS" and refused

  Scenario: A bulk address update file for a skeleton case is successfully ingested
    Given a NEW_ADDRESS_REPORTED event with address type "HH" is sent from "FIELD" and the case is created
    And a bulk address update file is supplied
    When the bulk address update file is processed
    Then CASE_UPDATED events are emitted for all the updated cases with correctly updated data and skeleton marker false
    And the cases are updated in the database
    And a CREATE message is sent to field for each updated case excluding NI CE cases and estab types "TRANSIENT PERSONS" and "MIGRANT WORKERS"

  Scenario: A bulk address un-invalidate file is successfully ingested
    Given sample file "sample_input_wales_census_spec.csv" is loaded successfully
    And all the cases are marked as invalid
    And a bulk un-invalidate addresses file is supplied
    When the bulk un-invalidate address file is processed
    Then CASE_UPDATED events are emitted for all the cases in the file with addressInvalid false
    And the addresses for the cases are un-invalidated in the database
    And an UPDATE message is sent to field for each updated case excluding NI CE, "TRANSIENT PERSONS" and refused

#    HERE BE DRAGONS! This is a hack which was forced onto us. Read more here: https://trello.com/c/i6xdQWau/1628-field-address-update-create-update-decision-hack-13
  Scenario: HACK 1: address update on new address from CC/RH with existing uprn (no sourceid, so no oa) (no coordid) -> CREATE
    Given a NEW_ADDRESS_REPORTED event is sent from "CC" without sourceCaseId and new case is emitted
    And a bulk address update file is supplied
    When the bulk address update file is processed
    Then CASE_UPDATED events are emitted for all the updated cases with correctly updated data and skeleton marker false
    And the cases are updated in the database
    And a CREATE message is sent to field for each updated case excluding NI CE cases and estab types "TRANSIENT PERSONS" and "MIGRANT WORKERS"

#    HERE BE DRAGONS! This is a hack which was forced onto us. Read more here: https://trello.com/c/i6xdQWau/1628-field-address-update-create-update-decision-hack-13
  Scenario: HACK 2: address update on new address from CC/RH with no uprn (no sourceid, so no oa)(no coordid) -> CREATE
    Given a NEW_ADDRESS_REPORTED event with no FieldCoordinatorId with address type "HH" is sent from "CC"
    And a bulk address update file is supplied
    When the bulk address update file is processed
    Then CASE_UPDATED events are emitted for all the updated cases with correctly updated data and skeleton marker false
    And the cases are updated in the database
    And a CREATE message is sent to field for each updated case excluding NI CE cases and estab types "TRANSIENT PERSONS" and "MIGRANT WORKERS"

#    HERE BE DRAGONS! This is a hack which was forced onto us. Read more here: https://trello.com/c/i6xdQWau/1628-field-address-update-create-update-decision-hack-13
  Scenario: HACK 3: address update on new address from CE/SPG field no sourceid (no oa) -> CREATE
    Given a NEW_ADDRESS_REPORTED event with no FieldCoordinatorId with address type "SPG" is sent from "CC"
    And a bulk address update file is supplied
    When the bulk address update file is processed
    Then CASE_UPDATED events are emitted for all the updated cases with correctly updated data and skeleton marker false
    And the cases are updated in the database
    And a CREATE message is sent to field for each updated case excluding NI CE cases and estab types "TRANSIENT PERSONS" and "MIGRANT WORKERS"

#    HERE BE DRAGONS! This is a hack which was forced onto us. Read more here: https://trello.com/c/i6xdQWau/1628-field-address-update-create-update-decision-hack-13
  Scenario: HACK 4: address update on new address from HH Field no sourceid -> CREATE
    Given a NEW_ADDRESS_REPORTED event with no FieldCoordinatorId with address type "HH" is sent from "FIELD"
    And a bulk address update file is supplied
    When the bulk address update file is processed
    Then CASE_UPDATED events are emitted for all the updated cases with correctly updated data and skeleton marker false
    And the cases are updated in the database
    And a CREATE message is sent to field for each updated case excluding NI CE cases and estab types "TRANSIENT PERSONS" and "MIGRANT WORKERS"

#    HERE BE DRAGONS! This is a hack which was forced onto us. Read more here: https://trello.com/c/i6xdQWau/1628-field-address-update-create-update-decision-hack-13
  Scenario: HACK 5: address update on new address from CE/SPG Field with sourceid. (has oa) (inc coord id)   [goes straight to field already] -> UPDATE
    Given sample file "sample_1_english_SPG_unit_with_fieldcoordinator.csv" is loaded successfully
    And a NEW_ADDRESS_REPORTED event is sent from "{sender}" with sourceCaseId and minimal event fields
    And a bulk address update file is supplied
    When the bulk address update file is processed
    Then CASE_UPDATED events are emitted for all the updated cases with correctly updated data and skeleton marker false
    And the cases are updated in the database
    And an UPDATE message is sent to field for each updated case excluding NI CE, "TRANSIENT PERSONS" and refused

#    HERE BE DRAGONS! This is a hack which was forced onto us. Read more here: https://trello.com/c/i6xdQWau/1628-field-address-update-create-update-decision-hack-13
  Scenario: HACK 6: address update on new address from HH Field with sourceid (For split address only) -> UPDATE
    Given sample file "sample_1_english_HH_unit_with_fieldcoordinator.csv" is loaded successfully
    And a NEW_ADDRESS_REPORTED event is sent from "{sender}" with sourceCaseId and minimal event fields
    And a bulk address update file is supplied
    When the bulk address update file is processed
    Then CASE_UPDATED events are emitted for all the updated cases with correctly updated data and skeleton marker false
    And the cases are updated in the database
    And an UPDATE message is sent to field for each updated case excluding NI CE, "TRANSIENT PERSONS" and refused

#    HERE BE DRAGONS! This is a hack which was forced onto us. Read more here: https://trello.com/c/i6xdQWau/1628-field-address-update-create-update-decision-hack-13
  Scenario: HACK 7: address update on new case created by address type change from CC (has oa) (no coordid) -> CREATE
    Given sample file "sample_1_english_HH_unit_with_fieldcoordinator.csv" is loaded successfully
    And an AddressTypeChanged event to "SPG" is sent
    And a case_updated msg is emitted where "addressInvalid" is "True"
    And a case created event is emitted
    And a bulk address update file is supplied
    When the bulk address update file is processed
    Then CASE_UPDATED events are emitted for all the updated cases with correctly updated data and skeleton marker false
    And the cases are updated in the database
    And a CREATE message is sent to field for each updated case excluding NI CE cases and estab types "TRANSIENT PERSONS" and "MIGRANT WORKERS"

#    HERE BE DRAGONS! This is a hack which was forced onto us. Read more here: https://trello.com/c/i6xdQWau/1628-field-address-update-create-update-decision-hack-13
  Scenario: HACK 8: address update on new case created by address type changed from CE/SPG (no coord id) -> CREATE
    Given sample file "sample_1_english_SPG_unit_with_fieldcoordinator.csv" is loaded successfully
    And an AddressTypeChanged event to "HH" is sent
    And a case_updated msg is emitted where "addressInvalid" is "True"
    And a case created event is emitted
    And a bulk address update file is supplied
    When the bulk address update file is processed
    Then CASE_UPDATED events are emitted for all the updated cases with correctly updated data and skeleton marker false
    And the cases are updated in the database
    And a CREATE message is sent to field for each updated case excluding NI CE cases and estab types "TRANSIENT PERSONS" and "MIGRANT WORKERS"
