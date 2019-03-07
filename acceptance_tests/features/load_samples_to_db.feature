#@skip
#Feature: Load Samples from file to database
#
#  Scenario: Successful sample file upload
#    Given a survey exists with a collection exercise
#    When sample file "Sample_10.csv" is loaded
#    Then the sample units are created and stored in the case service
