#@fixture.X
#@fixture.Y
#@fixture.Z
Feature: Load Samples from file to database

  @fixture.1
  @fixture.a
  @fixture.2
  @fixture.b
  @fixture.3
  @fixture.c
  @fixture.4
  @fixture.d
  @fixture.5
  @fixture.e
  Scenario: Good sample file load GSFL
    Given a collection exercise exists
    When a sample file "Sample_10.csv" is loaded
    Then a call to the casesvc api returns 10 cases

