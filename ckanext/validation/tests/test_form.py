import json

from nose.tools import assert_in, assert_equals


from ckantoolkit.tests.factories import Sysadmin, Dataset
from ckantoolkit.tests.helpers import (
    FunctionalTestBase, submit_and_follow, call_action, reset_db
)

from ckanext.validation.model import create_tables, tables_exist


def _get_resource_new_page_as_sysadmin(app, id):
    user = Sysadmin()
    env = {'REMOTE_USER': user['name'].encode('ascii')}
    response = app.get(
        url='/dataset/new_resource/{}'.format(id),
        extra_environ=env,
    )
    return env, response


def _get_resource_update_page_as_sysadmin(app, id, resource_id):
    user = Sysadmin()
    env = {'REMOTE_USER': user['name'].encode('ascii')}
    response = app.get(
        url='/dataset/{}/resource_edit/{}'.format(id, resource_id),
        extra_environ=env,
    )
    return env, response


class TestResourceSchemaForm(FunctionalTestBase):

    def setup(self):
        reset_db()
        if not tables_exist():
            create_tables()

    def test_resource_form_includes_json_fields(self):
        dataset = Dataset()

        app = self._get_test_app()
        env, response = _get_resource_new_page_as_sysadmin(app, dataset['id'])
        form = response.forms['resource-edit']
        assert_in('schema', form.fields)
        assert_equals(form.fields['schema'][0].tag, 'textarea')

    def test_resource_form_create(self):
        dataset = Dataset()

        app = self._get_test_app()
        env, response = _get_resource_new_page_as_sysadmin(app, dataset['id'])
        form = response.forms['resource-edit']

        value = {
            'fields': [
                {'name': 'code'},
                {'name': 'department'}
            ]
        }
        json_value = json.dumps(value)

        form['url'] = 'http://example.com/data.csv'
        form['schema'] = json_value

        submit_and_follow(app, form, env, 'save')

        dataset = call_action('package_show', id=dataset['id'])

        assert_equals(dataset['resources'][0]['schema'], value)

    def test_resource_form_update(self):
        value = {
            'fields': [
                {'name': 'code'},
                {'name': 'department'}
            ]
        }
        dataset = Dataset(
            resources=[{
                'url': 'http://example.com/data.csv',
                'schema': value
            }]
        )

        app = self._get_test_app()
        env, response = _get_resource_update_page_as_sysadmin(
            app, dataset['id'], dataset['resources'][0]['id'])
        form = response.forms['resource-edit']

        assert_equals(form['schema'].value, json.dumps(value, indent=2))

        value = {
            'fields': [
                {'name': 'code'},
                {'name': 'department'},
                {'name': 'date'}
            ]
        }

        json_value = json.dumps(value)

        form['schema'] = json_value

        submit_and_follow(app, form, env, 'save')

        dataset = call_action('package_show', id=dataset['id'])

        assert_equals(dataset['resources'][0]['schema'], value)
