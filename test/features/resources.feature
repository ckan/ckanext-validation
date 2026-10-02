@resources
Feature: Resource UI

    @format_autocomplete
    Scenario Outline: Link resource should create a link to its URL
        Given "SysAdmin" as the persona
        When I log in
        And I create a resource with name "<name>" and URL "<url>"
        And I press the element with xpath "//a[(contains(@title, '<name>') or contains(@aria-label, '<name>')) and contains(string(), '<name>')]"
        And I take a debugging screenshot
        Then I should see "<url>" within 2 seconds

        Examples:
        | name | url |
        | link | http://example.com |
