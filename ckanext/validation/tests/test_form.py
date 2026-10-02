# encoding: utf-8

import json

import six
import mock
import pytest
from bs4 import BeautifulSoup

from ckan.tests.factories import SysadminWithToken, Dataset
from ckan.tests.helpers import call_action

from ckanext.validation.tests.helpers import (
    NEW_SCHEMA,
    VALID_CSV,
    INVALID_CSV,
    SCHEMA,
    VALID_REPORT,
    MockFileStorage,
)

NEW_RESOURCE_URL = '/dataset/{}/resource/new'
EDIT_RESOURCE_URL = '/dataset/{}/resource/{}/edit'


def _get_resource_new_page_as_sysadmin(app, id):
    """Returns a resource create page response"""
    response = app.get(
        url=NEW_RESOURCE_URL.format(id),
        headers=_get_sysadmin_env(),
    )
    return response


def _get_resource_update_page_as_sysadmin(app, id, resource_id):
    """Returns a resource update page response"""
    response = app.get(
        url=EDIT_RESOURCE_URL.format(id, resource_id),
        headers=_get_sysadmin_env(),
    )
    return response


def _get_sysadmin_env():
    user = SysadminWithToken()
    return {"Authorization": user["token"]}


def _get_response_body(response):
    if hasattr(response, 'text'):
        return response.text
    else:
        return response.body


def _get_form(response):
    soup = BeautifulSoup(_get_response_body(response), 'html.parser')
    return soup.find('form', id='resource-edit')


def _post(app, url, params, upload=None):
    args = []

    params['save'] = ''
    params.setdefault('id', '')

    if upload:
        field_name = 0
        file_name = 1
        file_data = 2

        for entry in upload:
            params[entry[field_name]] = MockFileStorage(
                six.BytesIO(six.ensure_binary(entry[file_data])),
                entry[file_name])

    kwargs = {
        'url': url,
        'data': params,
        'headers': _get_sysadmin_env()
    }

    return app.post(*args, **kwargs)


@pytest.mark.usefixtures("clean_db", "validation_setup")
class TestResourceSchemaForm(object):

    def test_resource_form_includes_schema_fields(self, app):
        """All schema related fields must be in the resource form"""
        dataset = Dataset()

        response = _get_resource_new_page_as_sysadmin(app, dataset['id'])
        form = _get_form(response)

        assert form.find("input", attrs={'name': 'schema'})
        assert form.find("input", attrs={'name': 'schema_upload'})
        assert form.find("textarea", attrs={'name': 'schema_json'})
        assert form.find("input", attrs={'name': 'schema_url'})

    def test_resource_form_create_with_schema(self, app):
        """Test we are able to create a resource with a schema"""
        dataset = Dataset()

        params = {
            'name': 'test_resource_form_create',
            'package_id': dataset['id'],
            'schema': json.dumps(SCHEMA),
        }

        _post(app, NEW_RESOURCE_URL.format(dataset['id']), params)

        dataset = call_action('package_show', id=dataset['id'])

        assert dataset['resources'][0]['schema'] == SCHEMA

    def test_resource_form_create_schema_from_schema_json(self, app):
        """Test we are able to create a resource with schema from a json"""
        dataset = Dataset()

        params = {
            'name': 'test_resource_form_create_json',
            'package_id': dataset['id'],
            'url': 'https://example.com/data.csv',
            'schema_json': json.dumps(SCHEMA),
        }

        _post(app, NEW_RESOURCE_URL.format(dataset['id']), params)

        dataset = call_action('package_show', id=dataset['id'])

        assert dataset['resources'][0]['schema'] == SCHEMA

    def test_resource_form_create_schema_from_schema_upload(self, app):
        """Test we are able to create a resource with schema from an uploaded file"""
        dataset = Dataset()

        params = {
            'name': 'test_resource_form_create_upload',
            'package_id': dataset['id'],
            'url': 'https://example.com/data.csv',
        }

        _post(app,
              NEW_RESOURCE_URL.format(dataset['id']),
              params,
              upload=[('schema_upload', 'data.json', json.dumps(SCHEMA))])

        dataset = call_action('package_show', id=dataset['id'])

        assert dataset['resources'][0]['schema'] == SCHEMA

    def test_resource_form_create_schema_from_schema_url(
            self, app, mocked_responses):
        """Test we are able to create a resource with schema from a url"""
        dataset = Dataset()

        schema_url = 'https://example.com/schema.json'
        mocked_responses.add('GET', schema_url, json=SCHEMA)

        params = {
            'name': 'test_resource_form_create_url',
            'package_id': dataset['id'],
            'url': 'https://example.com/data.csv',
            'schema_url': schema_url,
        }

        _post(app, NEW_RESOURCE_URL.format(dataset['id']), params)

        dataset = call_action('package_show', id=dataset['id'])

        assert dataset['resources'][0]['schema'] == SCHEMA

    def test_resource_form_update_with_new_schema(self, app, resource_factory):
        """Test we are able to update a resource with a new schema"""
        dataset = Dataset()
        resource = resource_factory(package_id=dataset["id"])
        resource_id = resource["id"]

        assert resource['schema'] == SCHEMA

        params = {
            'id': resource["id"],
            'name': 'test_resource_form_update',
            'url': 'https://example.com/data.csv',
            'schema': json.dumps(NEW_SCHEMA)
        }

        _post(app, EDIT_RESOURCE_URL.format(dataset['id'], resource_id), params)

        resource = call_action('resource_show', id=resource_id)

        assert resource['schema'] == NEW_SCHEMA

    def test_resource_form_update_json(self, app, resource_factory):
        dataset = Dataset()
        resource = resource_factory(package_id=dataset['id'])
        resource_id = resource["id"]

        assert resource['schema'] == SCHEMA

        params = {'id': resource_id, 'schema_json': json.dumps(NEW_SCHEMA)}

        _post(app, EDIT_RESOURCE_URL.format(dataset['id'], resource_id), params)

        resource = call_action('resource_show', id=resource_id)

        assert resource['schema'] == NEW_SCHEMA

    def test_resource_form_update_url(self, app, resource_factory,
                                      mocked_responses):
        """Test we are able to replace a schema from a url to an existing resource"""
        dataset = Dataset()
        resource = resource_factory(package_id=dataset['id'])
        resource_id = resource["id"]

        assert resource['schema'] == SCHEMA

        schema_url = 'https://example.com/schema.json'
        mocked_responses.add('GET', schema_url, json=NEW_SCHEMA)
        params = {'id': resource_id, 'schema_url': schema_url}

        _post(app, EDIT_RESOURCE_URL.format(dataset['id'], resource_id), params)

        resource = call_action('resource_show', id=resource_id)

        assert resource['schema'] == NEW_SCHEMA

    def test_resource_form_update_upload(self, app, resource_factory):
        """Test we are able to replace a schema from a file for an existing resource"""
        dataset = Dataset()
        resource = resource_factory(package_id=dataset['id'])

        assert resource['schema'] == SCHEMA

        params = {
            'id': resource["id"],
        }

        _post(app,
              EDIT_RESOURCE_URL.format(dataset['id'], resource["id"]),
              params,
              upload=[('schema_upload', 'data.json', json.dumps(NEW_SCHEMA))])

        resource = call_action('resource_show', id=resource['id'])

        assert resource['schema'] == NEW_SCHEMA


@pytest.mark.usefixtures("clean_db", "validation_setup")
class TestResourceValidationOptionsForm(object):

    def test_resource_form_includes_validation_options_field(self, app):
        """validation_options must be in the resource form"""
        dataset = Dataset()

        response = _get_resource_new_page_as_sysadmin(app, dataset['id'])
        form = _get_form(response)

        assert form.find("textarea", attrs={'name': 'validation_options'})

    def test_resource_form_create(self, app):
        dataset = Dataset()

        value = {
            'delimiter': ',',
            'headers': 1,
        }
        json_value = json.dumps(value)
        params = {
            'name': 'test_resource_form_create',
            'url': 'https://example.com/data.csv',
            'validation_options': json_value,
        }

        _post(app, NEW_RESOURCE_URL.format(dataset['id']), params)

        dataset = call_action('package_show', id=dataset['id'])

        assert dataset['resources'][0]['validation_options'] == value

    def test_resource_form_update(self, app, resource_factory):
        options = {
            "dialect": {
                "header": True,
                "headerRows": [1],
                "commentChar": "#",
                "csv": {
                    "delimiter": ","
                }
            }
        }

        resource = resource_factory(validation_options=options)
        resource_id = resource['id']

        response = _get_resource_update_page_as_sysadmin(
            app, resource['package_id'], resource_id)
        form = _get_form(response)

        assert form.find("textarea",
                         attrs={'name': 'validation_options'}).text ==\
            json.dumps(options, indent=2, sort_keys=True)

        new_options = {
            "dialect": {
                "header": True,
                "headerRows": [4],
                "commentChar": "#",
                "csv": {
                    "delimiter": ","
                },
                "skip": ["blank-rows"]  # Skip blank rows (maps to `skip_tests`)
            }
        }

        params = {
            'id': resource_id,
            'name': 'test_resource_form_update',
            'url': 'https://example.com/data.csv',
            'validation_options': json.dumps(new_options)
        }

        _post(app, EDIT_RESOURCE_URL.format(resource['package_id'],
                                            resource_id), params)
        resource = call_action('resource_show', id=resource['id'])

        assert resource['validation_options'] == new_options

    def test_resource_form_update_goodtables_options(self, app, resource_factory):
        options = {
            'delimiter': ',',
            'headers': 1,
            'skip_rows': ['#'],
        }

        resource = resource_factory(validation_options=options)
        resource_id = resource['id']

        response = _get_resource_update_page_as_sysadmin(
            app, resource['package_id'], resource_id)
        form = _get_form(response)

        assert form.find("textarea",
                         attrs={'name': 'validation_options'}).text ==\
            json.dumps(options, indent=2, sort_keys=True)

        new_options = {
            'delimiter': ',',
            'headers': 4,
            'skip_rows': ['#'],
            'skip_tests': ['blank-rows'],
        }

        params = {
            'id': resource_id,
            'name': 'test_resource_form_update',
            'url': 'https://example.com/data.csv',
            'validation_options': json.dumps(new_options)
        }

        _post(app, EDIT_RESOURCE_URL.format(resource['package_id'],
                                            resource_id), params)
        resource = call_action('resource_show', id=resource['id'])

        assert resource['validation_options'] == new_options


@pytest.mark.usefixtures("clean_db", "validation_setup")
class TestResourceValidationOnCreateForm(object):

    def test_resource_form_create_valid(self, app):
        """Test we aren able to create resource with a valid CSV file.
        If schema and format is provided - resource will be validated according
        to the schema"""
        dataset = Dataset()

        params = {
            'name': 'test_resource_form_create_valid',
            'url': 'https://example.com/data.csv',
            'schema': json.dumps(SCHEMA),
            'format': 'csv'
        }

        _post(app,
              NEW_RESOURCE_URL.format(dataset['id']),
              params,
              upload=[('upload', 'data.csv', VALID_CSV)])

        dataset = call_action('package_show', id=dataset['id'])

        assert dataset['resources'][0]['validation_status'] == 'success'
        assert 'validation_timestamp' in dataset['resources'][0]

    def test_resource_form_create_invalid(self, app):
        """Test we aren't able to create resource with an ivalid CSV file.
        If schema and format is provided - resource will be validated according
        to the schema"""
        dataset = Dataset()

        params = {
            'name': 'test_resource_form_create_invalid',
            'url': 'https://example.com/data.csv',
            'schema': json.dumps(SCHEMA),
            'format': 'csv'
        }

        response = _get_response_body(
            _post(app,
                  NEW_RESOURCE_URL.format(dataset['id']),
                  params,
                  upload=[('upload', 'data.csv', INVALID_CSV)]))

        assert 'validation' in response
        assert 'missing-cell' in response
        assert ('Row at position \\&#34;2\\&#34; has a missing cell in field \\&#34;d\\&#34; at position \\&#34;4\\&#34;' in response)


@pytest.mark.usefixtures("clean_db", "validation_setup")
class TestResourceValidationOnUpdateForm(object):

    def test_resource_form_update_valid(self, app, resource_factory):
        """Test we are able to update resource with a valid CSV file.
        If schema and format is provided - resource will be validated according
        to the schema"""
        dataset = Dataset()
        resource = resource_factory(package_id=dataset['id'], format="PDF")

        params = {
            'id': resource["id"],
            'name': 'test_resource_form_update_invalid',
            'url': 'https://example.com/data.csv',
            'format': 'csv',
            'schema': json.dumps(SCHEMA)
        }

        response = _get_response_body(
            _post(app,
                  EDIT_RESOURCE_URL.format(dataset['id'], resource["id"]),
                  params,
                  upload=[('upload', 'data.csv', VALID_CSV)]))

        assert 'missing-cell' not in response

        assert ('has a missing cell in field' not in response)
        resource = call_action('resource_show', id=resource['id'])

        assert resource['validation_status'] == 'success'
        assert resource['validation_timestamp']

    def test_resource_form_update_invalid(self, app, resource_factory):
        """Test we aren't able to update resource with an invalid CSV file.
        If schema and format is provided - resource will be validated according
        to the schema"""
        dataset = Dataset()
        resource = resource_factory(package_id=dataset['id'])

        params = {
            'id': resource["id"],
            'format': 'csv',
            'schema': json.dumps(SCHEMA)
        }
        response = _get_response_body(
            _post(app,
                  EDIT_RESOURCE_URL.format(dataset['id'], resource["id"]),
                  params,
                  upload=[('upload', 'data.csv', INVALID_CSV)]))

        assert 'validation' in response
        assert 'missing-cell' in response
        assert ('Row at position \\&#34;2\\&#34; has a missing cell in field \\&#34;d\\&#34; at position \\&#34;4\\&#34;' in response)


@pytest.mark.usefixtures("clean_db", "validation_setup")
class TestResourceValidationFieldsPersisted(object):

    @mock.patch('ckanext.validation.jobs.validate', return_value=VALID_REPORT)
    def test_resource_form_fields_are_persisted(self, mock_report, app,
                                                resource_factory):
        dataset = Dataset()
        resource = resource_factory(package_id=dataset['id'], description="")

        assert resource['validation_status'] == 'success'
        assert not resource.get('description')

        params = {
            'id': resource['id'],
            'description': 'test desc',
            'url': 'https://example.com/data.xlsx',
            'format': 'xlsx',
            'schema': json.dumps(SCHEMA)
        }

        response_post = _post(app, EDIT_RESOURCE_URL.format(dataset['id'], resource['id']), params)
        resource = call_action('resource_show', id=resource['id'])

        assert resource['description'] == 'test desc'
        assert resource['validation_timestamp']
        assert resource['validation_status'] == 'success'

        assert '<th scope="row">Validation status</th>\n                <td>success</td>' in response_post.body
        assert '<th scope="row">Validation timestamp</th>\n                <td>' + resource['validation_timestamp'] + '</td>' in response_post.body
