Feature: Generate new UAC-QID pairs and associated event

  Scenario: Check a UAC QID pair can be generated
    When a UAC/QID pair is requested with a valid questionnaire type
    Then caseapi should return a new UAC and QID with correct questionnaire type