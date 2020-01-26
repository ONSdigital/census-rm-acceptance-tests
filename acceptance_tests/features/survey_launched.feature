#Feature: Handle survey launched event
#
#  Scenario: Survey launched message results in case event logged
#    Given sample file "sample_for_receipting.csv" is loaded successfully
#    When a survey launched for a created case is received
#    Then the events logged for the survey launched case are [SAMPLE_LOADED,SURVEY_LAUNCHED]