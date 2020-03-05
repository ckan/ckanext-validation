@smoke
Feature: Homepage

    @homepage
    Scenario: Smoke test to ensure Homepage is accessible
        When I go to homepage
        Then I take a screenshot