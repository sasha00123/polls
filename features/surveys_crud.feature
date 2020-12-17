Feature: Admins should be able to create/edit/delete surveys

  Scenario: Create survey
    Given admin is logged in

    When the request sends POST to /api/surveys/
    """
    {
      "title": "New survey",
      "description": "Very long description of the survey",
      "begin": "2001-09-15T16:46:00",
      "end": "2012-12-21T23:59:59"
    }
    """

    Then the response status is 201

  Scenario: Users should not be able to create surveys
    Given user is logged in

    When the request sends POST to /api/surveys/
    """
    {
      "title": "New survey",
      "description": "Very long description of the survey",
      "begin": "2001-09-15T16:46:00",
      "end": "2012-12-21T23:59:59"
    }
    """

    Then the response status is 403

  Scenario: Update survey
    Given admin is logged in
    And 1 surveys created

    When the request sends PATCH to /api/surveys/{{surveys.0.id}}
    """
    {
      "title": "Updated survey",
      "description": "New very long description of the survey."
    }
    """

    Then the response status is 200

  Scenario: Start time cannot be updated after creation
    Given admin is logged in
    And 1 surveys created with {"begin": "2001-09-15T16:46:00"}

    When the request sends PATCH to /api/surveys/{{surveys.0.id}}
    """
    {
      "title": "Updated survey",
      "description": "New very long description of the survey.",
      "begin": "2012-12-21T23:59:59"
    }
    """

    Then the response json at $.begin is equal to "2001-09-15 12:46:00+00:00"

  Scenario: Remove survey
    Given admin is logged in
    And 1 surveys created

    When the request sends DELETE to /api/surveys/{{surveys.0.id}}

    Then the response status is 204

  Scenario: Retrieve surveys
    Given admin is logged in
    And 3 surveys created

    When the request sends GET to /api/surveys/

    Then the response status is 200
    And the response json matches
    """
    {
      "title": "SurveyArray",
      "type": "array"
    }
    """
