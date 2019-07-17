Feature: Checks large file

  Scenario: Successful large sample file upload and England ICL print file
    Given an action rule of type ICL1E is set 600 seconds in the future
    When sample file "large_sample_file.csv" is loaded
    Then messages are emitted to RH and Action Scheduler with [01] qids
    And correctly formatted "P_IC_ICL1" print files are created
    And there is a correct "P_IC_ICL1" manifest file for each csv file written
    And events of pack code "P_IC_ICL1" are logged against the case