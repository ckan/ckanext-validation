from behave import step
from behaving.web.steps import *  # noqa: F401, F403
from behaving.personas.steps import *  # noqa: F401, F403
from behaving.web.steps.url import when_i_visit_url


@step('I go to homepage')
def go_to_home(context):
    when_i_visit_url(context, '/')


@step('I log in')
def log_in(context):

    assert context.persona
    context.execute_steps(u"""
        When I go to homepage
        And I click the link with text that contains "Log in"
        And I fill in "login" with "$name"
        And I fill in "password" with "$password"
        And I press the element with xpath "//button[contains(string(), 'Login')]"
        Then I should see an element with xpath "//a[contains(string(), 'Log out')]"
    """)


@step('I create a resource with name "{name}" and URL "{url}"')
def add_resource(context, name, url):
    context.execute_steps(u"""
        When I log in
        And I visit "/dataset/new_resource/warandpeace"
        And I press the element with xpath "//form[@id='resource-edit']//a[string() = 'Link']"
        And I fill in "name" with "{}"
        And I fill in "url" with "{}"
        And I press the element with xpath "//button[contains(string(), 'Add')]"
    """.format(name, url))


@step('I go to dataset page')
def go_to_dataset_page(context):
    when_i_visit_url(context, '/dataset')


@step('I go to organisation page')
def go_to_organisation_page(context):
    when_i_visit_url(context, '/organization')


@step('I go to register page')
def go_to_register_page(context):
    when_i_visit_url(context, '/user/register')


@step('I search the autocomplete API for user "{username}"')
def go_to_user_autocomplete(context, username):
    when_i_visit_url(context, '/api/2/util/user/autocomplete?q={}'.format(username))


@step('I go to the user list API')
def go_to_user_list(context):
    when_i_visit_url(context, '/api/3/action/user_list')


@step('I go to the "{user_id}" profile page')
def go_to_user_profile(context, user_id):
    when_i_visit_url(context, '/user/{}'.format(user_id))


@step('I go to the dashboard')
def go_to_dashboard(context):
    when_i_visit_url(context, '/dashboard')


@step('I go to the "{user_id}" user API')
def go_to_user_show(context, user_id):
    when_i_visit_url(context, '/api/3/action/user_show?id={}'.format(user_id))


@step('I view the "{group_id}" group API "{including}" users')
def go_to_group_including_users(context, group_id, including):
    when_i_visit_url(context, r'/api/3/action/group_show?id={}&include_users={}'.format(group_id, including in ['with', 'including']))


@step('I view the "{organisation_id}" organisation API "{including}" users')
def go_to_organisation_including_users(context, organisation_id, including):
    when_i_visit_url(context, r'/api/3/action/organization_show?id={}&include_users={}'.format(organisation_id, including in ['with', 'including']))
