Feature: survey service

  Scenario: create survey
    Given we need a survey
    When we call create survey endpoint
    Then we get 201 response

  Scenario: add survey classifiers
    Given we have a survey
    When we add classifiers
    Then we can load classifiers by survey