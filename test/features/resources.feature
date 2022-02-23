@resources
Feature: Resource UI

    @format_autocomplete
    Scenario Outline: Link resource should create a link to its URL
        Given "Admin" as the persona
        When I create a resource with name "<name>" and URL "<url>"
        And I press the element with xpath "//a[contains(@title, '<name>') and contains(string(), '<name>')]"
        Then I take a screenshot
        And I should see "<url>"

        Examples:
        | name | url |
        | link | http://example.com |
