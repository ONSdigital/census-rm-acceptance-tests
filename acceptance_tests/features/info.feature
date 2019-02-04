Feature: check info endpoints

  Scenario: check rm services are running
    Given we have rm services running
    When we call info endpoint
    Then we get 200 response