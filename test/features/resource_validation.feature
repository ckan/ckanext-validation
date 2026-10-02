@resource_validation
Feature: Resource validation

    Scenario: As an editor, I can create and update a resource with an uploaded validation schema
        Given "TestOrgEditor" as the persona
        When I log in
        And I create a dataset with key-value parameters "notes=Test uploaded schema"
        And I open the new resource form for dataset "$last_generated_name"
        And I upload "test.csv" of type "CSV" to resource
        And I fill in "name" with "Test validation schema"
        And I fill in "description" with "Testing validation schema"
        And I upload schema file "test_schema.json" to resource
        And I press the element with xpath "//button[contains(@class, 'btn-primary')]"
        Then I should see "Test validation schema" within 2 seconds

        When I click the link with text that contains "Test validation schema"
        And I press the element with xpath "//div[contains(@class, 'action')]//a[contains(@href, '/resource/') and contains(@href, '/edit')]"
        Then I should see text containing quotes `"fields": [`
        And I should see text containing quotes `"name": "field1"`
        And I should see text containing quotes `"name": "field2"`
        When I upload schema file "test_schema2.json" to resource
        And I press the element with xpath "//button[contains(@class, 'btn-primary')]"
        Then I should see "Test validation schema" within 2 seconds
        When I click the link with text that contains "Test validation schema"
        And I press the element with xpath "//div[contains(@class, 'action')]//a[contains(@href, '/resource/') and contains(@href, '/edit')]"
        Then I should see text containing quotes `"fields": [`
        And I should see text containing quotes `"name": "field1"`
        And I should see text containing quotes `"name": "field2"`
        And I should see text containing quotes `"title": "First column"`
        And I should see text containing quotes `"title": "Second column"`

    Scenario: As an editor, I can create and update a resource with validation options
        Given "TestOrgEditor" as the persona
        When I log in
        And I create a dataset with key-value parameters "notes=Test validation options"
        And I open the new resource form for dataset "$last_generated_name"
        And I upload "test.csv" of type "CSV" to resource
        And I fill in "name" with "Test validation options"
        And I fill in "description" with "Testing validation options"
        And I upload schema file "test_schema.json" to resource
        And I fill in "validation_options" with "{"headers": 1}"
        And I execute the script "document.getElementById('field-format').value='CSV'"
        And I press the element with xpath "//button[contains(@class, 'btn-primary')]"
        Then I should see "Test validation options" within 2 seconds

        When I click the link with text that contains "Test validation options"
        And I press the element with xpath "//div[contains(@class, 'action')]//a[contains(@href, '/resource/') and contains(@href, '/edit')]"
        Then I should see text containing quotes `"headers": 1`

        When I click the link with text that contains "Test validation options"
        And I press the element with xpath "//div[contains(@class, 'action')]//a[contains(@href, '/resource/') and contains(@href, '/edit')]"
        And I fill in "validation_options" with "{"delimiter": ","}"

        And I press the element with xpath "//button[contains(@class, 'btn-primary')]"
        Then I should see "Test validation options" within 2 seconds
        When I click the link with text that contains "Test validation options"
        And I press the element with xpath "//div[contains(@class, 'action')]//a[contains(@href, '/resource/') and contains(@href, '/edit')]"
        Then I should see text containing quotes `"delimiter": ","`

    Scenario: As an editor, I can create a resource with a valid CSV and see a success status
        Given "TestOrgEditor" as the persona
        When I log in
        And I create a dataset with key-value parameters "notes=Test valid CSV"
        And I open the new resource form for dataset "$last_generated_name"
        And I upload "test.csv" of type "CSV" to resource
        And I fill in "name" with "Test valid CSV create"
        And I upload schema file "test_schema.json" to resource
        And I fill in "description" with "Testing validation that should pass"
        And I execute the script "document.getElementById('field-format').value='CSV'"
        And I press the element with xpath "//button[contains(@class, 'btn-primary')]"
        Then I should see "Test valid CSV" within 2 seconds
        When I click the link with text that contains "Test valid CSV"
        Then I should see "Validation status" within 2 seconds
        And I should see "success" within 2 seconds
        And I should not see "failure" within 2 seconds
        And I should see a validation timestamp

    Scenario: As an editor, I can update a resource with a valid CSV and see a success status
        Given "TestOrgEditor" as the persona
        When I log in
        And I create a dataset with key-value parameters "notes=Test valid CSV"
        And I open the new resource form for dataset "$last_generated_name"
        And I upload "invalid.csv" of type "CSV" to resource
        And I fill in "name" with "Test valid CSV update"
        And I fill in "description" with "Testing validation that should pass on update"
        And I press the element with xpath "//button[contains(@class, 'btn-primary')]"
        Then I should see "Test valid CSV update" within 2 seconds
        When I click the link with text that contains "Test valid CSV update"
        And I press the element with xpath "//div[contains(@class, 'action')]//a[contains(@href, '/resource/') and contains(@href, '/edit')]"
        And I upload "test.csv" of type "CSV" to resource
        And I upload schema file "test_schema.json" to resource
        And I press the element with xpath "//button[contains(@class, 'btn-primary')]"
        And I click the link with text that contains "Test valid CSV update"
        Then I should see "Validation status" within 2 seconds
        And I should see "success" within 2 seconds
        And I should not see "failure" within 2 seconds
        And I should see a validation timestamp

    Scenario: As an editor, I can update a resource with an invalid CSV and see a validation error
        Given "TestOrgEditor" as the persona
        When I log in
        And I create a dataset with key-value parameters "notes=Test invalid CSV"
        And I open the new resource form for dataset "$last_generated_name"
        And I upload "test.csv" of type "CSV" to resource
        And I fill in "name" with "Test invalid CSV update"
        And I upload schema file "test_schema.json" to resource
        And I fill in "description" with "Testing validation that should fail on update"
        And I press the element with xpath "//button[contains(@class, 'btn-primary')]"
        Then I should see "Test invalid CSV update" within 2 seconds
        When I click the link with text that contains "Test invalid CSV update"
        And I press the element with xpath "//div[contains(@class, 'action')]//a[contains(@href, '/resource/') and contains(@href, '/edit')]"
        And I upload "invalid.csv" of type "CSV" to resource
        And I press the element with xpath "//button[contains(@class, 'btn-primary')]"
        Then I should see "The form contains invalid entries" within 2 seconds
        And I should see "There are validation issues with this file" within 2 seconds
        When I click the link with text that contains "report"
        Then I should see "Validation Report" within 2 seconds
        And I should see "Incorrect Label" within 2 seconds
        And I should see "Extra Label" within 2 seconds
        And I should see "Extra Cell" within 2 seconds
