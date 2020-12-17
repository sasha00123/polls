Feature: Admins should be able to create/edit/update questions

  Scenario: Create questions
    Given admin is logged in
    And 1 surveys created

    When the request sends POST to /api/questions/
    """
    {
      "text": "New question",
      "type": "m_ch",
      "survey": {{surveys.0.id}},
      "options": [
          {"value": "First", "is_correct": true},
          {"value": "Second", "is_correct": false},
          {"value": "Third", "is_correct": false}
      ]
    }
    """

    Then the response status is 201

  Scenario: Users cannot create questions
    Given user is logged in
    And 1 surveys created


    When the request sends POST to /api/questions/
    """
    {
      "text": "New question",
      "type": "m_ch",
      "survey": {{surveys.0.id}},
      "options": [
          {"value": "First", "is_correct": true},
          {"value": "Second", "is_correct": false},
          {"value": "Third", "is_correct": false}
      ]
    }
    """

    Then the response status is 403

  Scenario: Update question
    Given admin is logged in
    And 1 surveys created
    And 1 questions created

    When the request sends PATCH to /api/questions/{{questions.0.id}}
    """
    {
      "text": "New question updated",
      "type": "m_ch",
      "survey": {{surveys.0.id}},
      "options": [
          {"value": "First", "is_correct": false},
          {"value": "Second", "is_correct": true},
          {"value": "Third", "is_correct": false}
      ]
    }
    """

    Then the response status is 200

  Scenario: Remove question
    Given admin is logged in
    And 1 surveys created
    And 1 questions created

    When the request sends DELETE to /api/questions/{{questions.0.id}}

    Then the response status is 204

  Scenario: Retrieve questions
    Given admin is logged in
    And 1 surveys created
    And 1 questions created

    When the request sends GET to /api/questions/{{questions.0.id}}

    Then the response status is 200
