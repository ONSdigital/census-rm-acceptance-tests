Feature: Load Samples from file to database

  @fixture.create.survey
#  @fixture.collection.exercise
  Scenario: Good sample file load GSFL
#    Given a collection exercise exists
    When a sample file "Sample_10.csv" is loaded
    Then a call to the casesvc api returns 10 cases

