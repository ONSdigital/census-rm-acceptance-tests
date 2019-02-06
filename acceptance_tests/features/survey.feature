Feature: survey service

  Scenario: create survey
    Given we need a survey
    When we call create survey endpoint
    Then we get 201 response