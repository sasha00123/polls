Feature: Allow users to create accounts and login.

  Scenario: Users should be able to create an account
    When the request sends POST to /api/register
    """
    {
      "username": "user",
      "password": "pass"
    }
    """

    Then the response status is 201

  Scenario: Users should be able to update their password
    Given user is logged in
    When the request sends PATCH to /api/set-password
    """
    {
      "old_password": "pass",
      "new_password": "pass2"
    }
    """
    Then the response status is 200

  Scenario: Users should be able to access their info
    Given user is logged in

    When the request sends GET to /api/account

    Then the response status is 200

  Scenario: Users should be able to receive a JWT token using their credentials.
    Given an account was created with username "user" and password "pass"

    When the request sends POST to /api/token/obtain
    """
    {
      "username": "user",
      "password": "pass"
    }
    """

    Then the response status is 200
    And the response json matches
    """
    {
      "title": "TokenObject",
      "type": "object",
      "properties": {
        "access": {"type": "string"},
        "refresh": {"type": "string"}
      },
      "required": ["access", "refresh"]
    }
    """