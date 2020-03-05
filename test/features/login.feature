@smoke @login
Feature: Login

    Scenario: Smoke test to ensure Login process works
        Given "Admin" as the persona
        When I go to homepage
        And I click the link with text that contains "Log in"
        And I fill in "login" with "$name"
        And I fill in "password" with "$password"
        # Login is a button without "name" or "id".
        And I press the element with xpath "//button[contains(string(), 'Login')]"
        And I take a screenshot
        Then I should see an element with xpath "//a[contains(string(), 'Log out')]"

    Scenario: Smoke test to ensure Login step works
        Given "Admin" as the persona
        When I log in
        Then I take a screenshot