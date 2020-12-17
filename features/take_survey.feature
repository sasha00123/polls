Feature: Users should be able to take a survey

  Scenario: Users should be able to take a survey
    Given admin is logged in
    And 1 surveys created
    And 1 questions created with {"type": "open"}
    And 1 questions created with {"type": "s_ch"}
    And 1 questions created with {"type": "m_ch"}
    And user is logged in

    When the request sends PATCH to /api/take-survey/{{surveys.0.id}}
    """
    {
      "answers": [
          {"answers": "[\"correct\"]", "question": {{questions.0.id}}},
          {"answers": "[\"{{questions.1.options.first.id}}\"]", "question": {{questions.1.id}}},
          {"answers": "[\"{{questions.2.options.first.id}}\", \"{{questions.2.options.last.id}}\"]", "question": {{questions.2.id}}}
      ]
    }
    """

    Then the response status is 200
    And the response json matches
    """
    {
      "title": "SuccessArray",
      "type": "object",
      "properties": {
        "answers": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
                "answers": {"type": "string"},
                "is_valid": {"type": "boolean"},
                "created": {"type": "string", "format": "date-time"},
                "question": {"type": "number"}
            }
          }
        }
      }
    }
    """
    And the response json at $.answers.0.is_valid is equal to true
    And the response json at $.answers.1.is_valid is equal to true
    And the response json at $.answers.2.is_valid is equal to false

  Scenario: Anonymous users should be able to take a survey
    Given admin is logged in
    And 1 surveys created
    And 1 questions created with {"type": "open"}
    And 1 questions created with {"type": "s_ch"}
    And 1 questions created with {"type": "m_ch"}
    And user is logged out

    When the request sends PATCH to /api/take-survey/{{surveys.0.id}}
    """
    {
      "answers": [
          {"answers": "[\"correct\"]", "question": {{questions.0.id}}},
          {"answers": "[\"{{questions.1.options.first.id}}\"]", "question": {{questions.1.id}}},
          {"answers": "[\"{{questions.2.options.first.id}}\", \"{{questions.2.options.last.id}}\"]", "question": {{questions.2.id}}}
      ]
    }
    """

    Then the response status is 200
    And the response json matches
    """
    {
      "title": "SuccessArray",
      "type": "object",
      "properties": {
        "answers": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
                "answers": {"type": "string"},
                "is_valid": {"type": "boolean"},
                "created": {"type": "null"},
                "question": {"type": "number"}
            }
          }
        }
      }
    }
    """
    And the response json at $.answers.0.is_valid is equal to true
    And the response json at $.answers.1.is_valid is equal to true
    And the response json at $.answers.2.is_valid is equal to false

  Scenario: Attempts should be available to user
    Given admin is logged in
    And 1 surveys created
    And 1 questions created with {"type": "open"}
    And 1 questions created with {"type": "s_ch"}
    And 1 questions created with {"type": "m_ch"}
    And user is logged in

    When the request sends PATCH to /api/take-survey/{{surveys.0.id}}
    """
    {
      "answers": [
          {"answers": "[\"correct\"]", "question": {{questions.0.id}}},
          {"answers": "[\"{{questions.1.options.first.id}}\"]", "question": {{questions.1.id}}},
          {"answers": "[\"{{questions.2.options.first.id}}\", \"{{questions.2.options.last.id}}\"]", "question": {{questions.2.id}}}
      ]
    }
    """
    And the request sends GET to /api/account

    Then the response status is 200
    And the response json matches
    """
    {
      "title": "MyDetails",
      "type": "object",
      "properties": {
        "username": {"type": "string"},
        "submissions": {"type": "array"}
      }
    }
    """
