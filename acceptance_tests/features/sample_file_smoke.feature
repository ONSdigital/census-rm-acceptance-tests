#@smoke_test
#Feature: Smoke tests to check the system is tied together correctly
#
#  Scenario: Successful sample file upload and England print file
#    Given an action rule of type ICL1E is set 10 seconds in the future
#    When sample file "sample_input_census_spec.csv" is loaded
#    Then messages are emitted to RH and Action Scheduler
#    And correctly formatted "P_IC_ICL1" print files are created
#    And there is a correct "P_IC_ICL1" manifest file for each csv file written
#
#  Scenario: Successful sample file upload and Wales print file
#    Given an action rule of type ICL2E is set 10 seconds in the future
#    When sample file "sample_input_census_spec.csv" is loaded
#    Then messages are emitted to RH and Action Scheduler
#    And correctly formatted "P_IC_ICL2" print files are created
#    And there is a correct "P_IC_ICL2" manifest file for each csv file written