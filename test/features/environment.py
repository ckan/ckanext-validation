# encoding: utf-8

import os

from behaving import environment as benv
from splinter.browser import Browser

# Path to the root of the project.
ROOT_PATH = os.path.realpath(os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    '../../'))

# Base URL for relative paths resolution.
BASE_URL = 'http://ckan:5000/'

# URL of remote Chrome instance.
REMOTE_CHROME_URL = 'http://chrome:4444/wd/hub'

# @see bin/init.sh for credentials.
PERSONAS = {
    'SysAdmin': {
        'name': u'admin',
        'email': u'admin@localhost',
        'password': u'Password123!'
    },
    'Unauthenticated': {
        'name': u'',
        'email': u'',
        'password': u''
    },
    'Organisation Admin': {
        'name': u'organisation_admin',
        'email': u'organisation_admin@localhost',
        'password': u'Password123!'
    },
    'Group Admin': {
        'name': u'group_admin',
        'email': u'group_admin@localhost',
        'password': u'Password123!'
    },
    'TestOrgAdmin': {
        'name': u'test_org_admin',
        'email': u'test_org_admin@localhost',
        'password': u'Password123!'
    },
    'TestOrgEditor': {
        'name': u'test_org_editor',
        'email': u'test_org_editor@localhost',
        'password': u'Password123!'
    },
    'TestOrgMember': {
        'name': u'test_org_member',
        'email': u'test_org_member@localhost',
        'password': u'Password123!'
    },
}


def before_all(context):
    # The path where screenshots will be saved.
    context.screenshots_dir = os.path.join(ROOT_PATH, 'test/screenshots')
    # The path where file attachments can be found.
    context.attachment_dir = os.path.join(ROOT_PATH, 'test/fixtures')

    # Set base url for all relative links.
    context.base_url = BASE_URL

    # Set the rest of the settings to default Behaving's settings.
    benv.before_all(context)


def after_all(context):
    benv.after_all(context)


def before_feature(context, feature):
    benv.before_feature(context, feature)


def after_feature(context, feature):
    benv.after_feature(context, feature)


def before_scenario(context, scenario):
    benv.before_scenario(context, scenario)
    # Always use remote browser.
    remote_browser = Browser(
        driver_name="remote", browser="chrome",
        command_executor=REMOTE_CHROME_URL
    )
    for persona_name in PERSONAS.keys():
        context.browsers[persona_name] = remote_browser
    # Set personas.
    context.personas = PERSONAS


def after_scenario(context, scenario):
    os.system("ckan jobs clear")
    benv.after_scenario(context, scenario)
