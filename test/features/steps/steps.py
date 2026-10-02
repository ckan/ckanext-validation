import uuid

from behave import when, then
from behaving.personas.steps import *  # noqa: F401, F403
from behaving.web.steps import *  # noqa: F401, F403
from behaving.web.steps.basic import should_see_within_timeout

# Monkey-patch Behaving to handle function rename
from behaving.web.steps import forms
if not hasattr(forms, 'fill_in_elem_by_name'):
    forms.fill_in_elem_by_name = forms.i_fill_in_field


dataset_default_schema = """
    {"fields": [
        {"format": "default", "name": "Game Number", "type": "integer"},
        {"format": "default", "name": "Game Length", "type": "integer"}
    ],
    "missingValues": ["Default schema"]
    }
"""

resource_default_schema = """
    {"fields": [
        {"format": "default", "name": "Game Number", "type": "integer"},
        {"format": "default", "name": "Game Length", "type": "integer"}
    ],
    "missingValues": ["Resource schema"]
    }
"""


@when(u'I take a debugging screenshot')
def debug_screenshot(context):
    """ Take a screenshot only if debugging is enabled in the persona.
    """
    if context.persona and context.persona.get('debug') == 'True':
        context.execute_steps(u"""
            When I take a screenshot
        """)


@when(u'I go to homepage')
def go_to_home(context):
    context.execute_steps(u"""
        When I visit "/"
    """)


@then(u'I should see text containing quotes `{text}`')
def should_see_backquoted(context, text):
    should_see_within_timeout(context, text, 5)


@when(u'I go to register page')
def go_to_register_page(context):
    context.execute_steps(u"""
        When I go to homepage
        And I press "Register"
    """)


@when(u'I log in')
def log_in(context):
    context.execute_steps(u"""
        When I go to homepage
        And I expand the browser height
        And I press "Log in"
        And I log in directly
    """)


@when(u'I expand the browser height')
def expand_height(context):
    # Work around x=null bug in Selenium set_window_size
    context.browser.driver.set_window_rect(x=0, y=0, width=1366, height=3072)


@when(u'I log in directly')
def log_in_directly(context):
    """
    This differs to the `log_in` function above by logging in directly to a page where the user login form is presented
    :param context:
    :return:
    """

    assert context.persona, "A persona is required to log in, found [{}] in context." \
        " Have you configured the personas in before_scenario?".format(context.persona)
    context.execute_steps(u"""
        When I attempt to log in with password "$password"
        Then I should see an element with xpath "//*[@title='Log out' or @data-bs-title='Log out']/i[contains(@class, 'fa-sign-out')]"
    """)


@when(u'I attempt to log in with password "{password}"')
def attempt_login(context, password):
    assert context.persona
    context.execute_steps(u"""
        When I fill in "login" with "$name"
        And I fill in "password" with "{}"
        And I press the element with xpath "//button[contains(string(), 'Login')]"
    """.format(password))


@when(u'I fill in "{name}" with "{value}" if present')
def fill_in_field_if_present(context, name, value):
    context.execute_steps(u"""
        When I execute the script "field = $('#{0}'); if (!field.length) field = $('[name={0}]'); if (!field.length) field = $('#field-{0}'); field.val('{1}'); field.keyup();"
    """.format(name, value.replace("'", r"\'")))


@when(u'I clear the URL field')
def clear_url(context):
    context.execute_steps(u"""
        When I execute the script "$('a.btn-remove-url:contains(Clear)').click();"
    """)


@when(u'I open the new resource form for dataset "{name}"')
def go_to_new_resource_form(context, name):
    context.execute_steps(u"""
        When I edit the "{0}" dataset
    """.format(name))
    if context.browser.is_element_present_by_xpath("//*[contains(@class, 'btn-primary') and contains(string(), 'Next:')]", wait_time=2):
        # Draft dataset, proceed directly to resource form
        context.execute_steps(u"""
            When I press "Next:"
        """)
    elif context.browser.is_element_present_by_xpath("//*[contains(string(), 'Add new resource')]"):
        # Existing dataset, browse to the resource form
        context.execute_steps(u"""
            When I press "Add new resource"
        """)
    else:
        # Existing dataset, browse to the resource form
        if context.browser.is_element_present_by_xpath(
                "//a[contains(string(), 'Resources') and contains(@href, '/dataset/resources/')]", wait_time=2):
            context.execute_steps(u"""
                When I press "Resources"
            """)
        context.execute_steps(u"""
            When I press "Add new resource"
            And I take a debugging screenshot
        """)


@when(u'I fill in title with random text')
def title_random_text(context):
    context.execute_steps(u"""
        When I fill in title with random text starting with "Test Title "
    """)


@when(u'I fill in title with random text starting with "{prefix}"')
def title_random_text_with_prefix(context, prefix):
    random_text = str(uuid.uuid4())
    title = prefix + random_text
    name = prefix.lower().replace(" ", "-") + random_text
    assert context.persona
    context.execute_steps(f"""
        When I fill in "title" with "{title}"
        And I fill in "name" with "{name}" if present
        And I set "last_generated_title" to "{title}"
        And I set "last_generated_name" to "{name}"
        And I take a debugging screenshot
    """)


@when(u'I create a resource with name "{name}" and URL "{url}"')
def add_resource(context, name, url):
    context.execute_steps(u"""
        When I create a dataset and resource with key-value parameters "notes=Link testing" and "name={name}::url={url}"
    """.format(name=name, url=url))


@when(u'I go to dataset page')
def go_to_dataset_page(context):
    context.execute_steps(u"""
        When I visit "/dataset"
    """)


@when(u'I go to dataset "{name}"')
def go_to_dataset(context, name):
    context.execute_steps(u"""
        When I visit "/dataset/{0}"
        And I take a debugging screenshot
    """.format(name))


@when(u'I edit the "{name}" dataset')
def edit_dataset(context, name):
    context.execute_steps(u"""
        When I go to dataset "{0}"
        And I press the element with xpath "//div[contains(@class, 'action')]//a[contains(@href, '/dataset/edit/')]"
    """.format(name))


@when(u'I select the "{licence_id}" licence')
def select_licence(context, licence_id):
    # Licence requires special interaction due to fancy JavaScript
    context.execute_steps(u"""
        When I execute the script "$('#field-license_id').val('{0}').trigger('change')"
    """.format(licence_id))


@when(u'I select the organisation with title "{title}"')
def select_organisation(context, title):
    # Organisation requires special interaction due to fancy JavaScript
    context.execute_steps(u"""
        When I execute the script "org_uuid=$('#field-organizations').find('option:contains({0})').val(); $('#field-organizations').val(org_uuid).trigger('change')"
        And I take a debugging screenshot
    """.format(title))


@when(u'I enter the resource URL "{url}"')
def enter_resource_url(context, url):
    if url != "default":
        context.execute_steps(u"""
            When I clear the URL field
            And I execute the script "$('#resource-edit [name=url]').val('{0}')"
        """.format(url))


@when(u'I fill in default dataset fields')
def fill_in_default_dataset_fields(context):
    context.execute_steps(u"""
        When I fill in title with random text
        And I fill in "notes" with "Description"
        And I fill in "version" with "1.0"
        And I fill in "author_email" with "test@me.com"
        And I select the "other-open" licence
        And I fill in "de_identified_data" with "NO" if present
    """)


@when(u'I fill in default resource fields')
def fill_in_default_resource_fields(context):
    context.execute_steps(u"""
        When I fill in "name" with "Test Resource"
        And I fill in "description" with "Test Resource Description"
        And I fill in "size" with "1024" if present
    """)


@when(u'I fill in link resource fields')
def fill_in_default_link_resource_fields(context):
    context.execute_steps(u"""
        When I enter the resource URL "https://example.com"
        And I execute the script "document.getElementById('field-format').value='HTML'"
        And I fill in "size" with "1024" if present
    """)


@when(u'I upload "{file_name}" of type "{file_format}" to resource')
def upload_file_to_resource(context, file_name, file_format):
    context.execute_steps(u"""
        When I execute the script "$('.resource-upload-field .btn-remove-url').trigger('click'); $('#resource-upload-button').trigger('click');"
        And I attach the file "{file_name}" to "upload"
        # Don't quote the injected string since it can have trailing spaces
        And I execute the script "document.getElementById('field-format').value='{file_format}'"
        And I fill in "size" with "1024" if present
    """.format(file_name=file_name, file_format=file_format))


@when(u'I upload schema file "{file_name}" to resource')
def upload_schema_file_to_resource(context, file_name):
    context.execute_steps(u"""
        When I execute the script "$('div[data-module=resource-schema] a.btn-remove-url').trigger('click'); $('input[name=schema_upload]').show().parent().show().parent().show();"
        And I attach the file "{file_name}" to "schema_upload"
    """.format(file_name=file_name))


@when(u'I go to organisation page')
def go_to_organisation_page(context):
    context.execute_steps(u"""
        When I visit "/organization"
    """)


@when(u'I search the autocomplete API for user "{username}"')
def go_to_user_autocomplete(context, username):
    context.execute_steps(u"""
        When I visit "/api/2/util/user/autocomplete?q={0}"
    """.format(username))


@when(u'I go to the user list API')
def go_to_user_list(context):
    context.execute_steps(u"""
        When I visit "/api/3/action/user_list"
    """)


@when(u'I go to the "{user_id}" profile page')
def go_to_user_profile(context, user_id):
    context.execute_steps(u"""
        When I visit "/user/{0}"
    """.format(user_id))


@when(u'I go to the dashboard')
def go_to_dashboard(context):
    context.execute_steps(u"""
        When I visit "/dashboard/datasets"
    """)


@then(u'I should see my datasets')
def dashboard_datasets(context):
    context.execute_steps(u"""
        Then I should see an element with xpath "//li[contains(@class, 'active') and contains(string(), 'My Datasets')]"
    """)


@when(u'I go to the "{user_id}" user API')
def go_to_user_show(context, user_id):
    context.execute_steps(u"""
        When I visit "/api/3/action/user_show?id={0}"
    """.format(user_id))


@when(u'I view the "{group_id}" {group_type} API "{including}" users')
def go_to_group_including_users(context, group_id, group_type, including):
    if group_type == "organisation":
        group_type = "organization"
    context.execute_steps(u"""
        When I visit "/api/3/action/{1}_show?id={0}&include_users={2}"
    """.format(group_id, group_type, including in ['with', 'including']))


# Parse a "key=value::key2=value2" parameter string and return an iterator of (key, value) pairs.
def _parse_params(param_string):
    params = {}
    for param in param_string.split("::"):
        entry = param.split("=", 1)
        params[entry[0]] = entry[1] if len(entry) > 1 else ""
    return params.items()


# Enter a JSON schema value
# This can require JavaScript interaction, and doesn't fit well into
# a step invocation due to all the double quotes.
def _enter_manual_schema(context, schema_json):
    # Click the button to select manual JSON input if it exists
    context.execute_steps(u"""
        When I execute the script "$('a.btn[title*=JSON]:contains(JSON)').click();"
    """)
    # Call function directly so we can properly quote our parameter
    forms.fill_in_elem_by_name(context, "schema_json", schema_json)


def _create_dataset_from_params(context, params):
    context.execute_steps(u"""
        When I visit "/dataset/new"
        And I fill in default dataset fields
    """)
    if 'private' not in params:
        params = params + "::private=False"
    for key, value in _parse_params(params):
        if key == "name":
            # 'name' doesn't need special input, but we want to remember it
            context.execute_steps(u"""
                When I set "last_generated_name" to "{0}"
            """.format(value))

        # Don't use elif here, we still want to type 'name' as usual
        if key == "owner_org":
            # Owner org uses UUIDs as its values, so we need to rely on displayed text
            context.execute_steps(u"""
                When I select the organisation with title "{0}"
            """.format(value))
        elif key in ["update_frequency", "request_privacy_assessment", "private"]:
            context.execute_steps(u"""
                When I select "{1}" from "{0}"
            """.format(key, value))
        elif key == "license_id":
            context.execute_steps(u"""
                When I select the "{0}" licence
            """.format(value))
        elif key == "schema_json":
            if value == "default":
                value = dataset_default_schema
            _enter_manual_schema(context, value)
        else:
            context.execute_steps(u"""
                When I fill in "{0}" with "{1}" if present
            """.format(key, value))
    context.execute_steps(u"""
        When I take a debugging screenshot
        And I press "Add Data"
        Then I should see "Add New Resource"
    """)


@when(u'I create a dataset with key-value parameters "{params}"')
def create_dataset_from_params(context, params):
    _create_dataset_from_params(context, params)
    context.execute_steps(u"""
        When I go to dataset "$last_generated_name"
    """)


@when(u'I create a dataset and resource with key-value parameters "{params}" and "{resource_params}"')
def create_dataset_and_resource_from_params(context, params, resource_params):
    _create_dataset_from_params(context, params)
    context.execute_steps(u"""
        When I create a resource with key-value parameters "{0}"
        Then I should see "Data and Resources"
    """.format(resource_params))


def _is_truthy(text):
    return text and text.lower() in ["true", "t", "yes", "y"]


def _get_yn_value(value, y_value="TRUE", n_value="FALSE"):
    return y_value if _is_truthy(value) else n_value


# Creates a resource using default values apart from the ones specified.
# The browser should already be on the create/edit resource page.
@when(u'I create a resource with key-value parameters "{resource_params}"')
def create_resource_from_params(context, resource_params):
    context.execute_steps(u"""
        When I fill in default resource fields
        And I fill in link resource fields
    """)
    for key, value in _parse_params(resource_params):
        if key == "url":
            context.execute_steps(u"""
                When I enter the resource URL "{0}"
            """.format(value))
        elif key == "upload":
            if value == "default":
                value = "test_game_data.csv"
            context.execute_steps(u"""
                When I clear the URL field
                And I execute the script "$('#resource-upload-button').click();"
                And I attach the file "{0}" to "upload"
            """.format(value))
        elif key == "format":
            context.execute_steps(u"""
                When I execute the script "document.getElementById('field-format').value='{0}'"
            """.format(value))
        elif key == "schema":
            if value == "default":
                value = resource_default_schema
            _enter_manual_schema(context, value)
        elif key == "schema_upload":
            if value == "default":
                value = "test-resource_schemea.json"
            context.execute_steps(u"""
                When I upload schema file "{0}" to resource
            """.format(value))
        else:
            context.execute_steps(u"""
                When I fill in "{0}" with "{1}" if present
            """.format(key, value))
    context.execute_steps(u"""
        When I take a debugging screenshot
        And I press the element with xpath "//form[contains(@data-module, 'resource-form')]//button[contains(@class, 'btn-primary')]"
        And I take a debugging screenshot
    """)


# ckanext-validation


@then(u'I should see a validation timestamp')
def should_see_validation_timestamp(context):
    context.execute_steps(u"""
        Then I should see "Validation timestamp" within 2 seconds
        And I should see an element with xpath "//th[contains(string(), 'Validation timestamp')]/../td[contains(string(), '-') and contains(string(), ':') and contains(string(), '.')]"
    """)
