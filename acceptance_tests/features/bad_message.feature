Feature: identify bad messages

  Scenario: Bad messages on RM queues are put on redelivery queue
    Given queues are free of messages
    When a bad message is placed on each of the queues
    Then the hash of the bad message is seen multiple times
    And queues are free of messages