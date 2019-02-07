Feature: collection exercise service

  Scenario: create collection exercise
    Given a survey exists
    When we create a collection exercise
    Then collection exercise id is created