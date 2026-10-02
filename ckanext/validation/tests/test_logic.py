# encoding: utf-8

import datetime
import io
import json

import responses
import mock
import six
import pytest

from ckan import model
from ckan.model import Session
from ckan.plugins import toolkit as tk
from ckan.tests.helpers import call_action, call_auth
from ckan.tests import factories

from ckanext.validation.model import Validation
from .helpers import (
    VALID_CSV,
    INVALID_CSV,
    LATIN1_CSV,
    SCHEMA,
    VALID_REPORT,
    MockFileStorage,
)


@pytest.mark.usefixtures("clean_db", "validation_setup")
class TestResourceValidationRun(object):

    def test_resource_validation_run_param_missing(self):
        with pytest.raises(tk.ValidationError) as err:
            call_action('resource_validation_run')

        assert err.value.error_dict == {'resource_id': 'Missing value'}

    def test_resource_validation_run_not_exists(self):
        with pytest.raises(tk.ObjectNotFound):
            call_action('resource_validation_run', resource_id='not_exists')

    def test_resource_validation_wrong_format(self):
        resource = factories.Resource(format='pdf', schema=SCHEMA)

        with pytest.raises(tk.ValidationError) as err:
            call_action('resource_validation_run', resource_id=resource['id'])

        assert 'Unsupported resource format' in err.value.error_dict['format']

    def test_resource_validation_no_url_or_upload(self):
        resource = factories.Resource(url='', format='csv', schema=SCHEMA)

        with pytest.raises(tk.ValidationError) as err:
            call_action('resource_validation_run', resource_id=resource['id'])

        assert {u'url':
                u'Resource must have a valid URL or an uploaded file'} ==\
            err.value.error_dict

    def test_resource_validation_with_url(self, mocked_responses):
        url = 'http://example.com'
        mocked_responses.add(responses.GET, url, body=VALID_CSV, stream=True)
        resource = factories.Resource(url=url, format='csv', schema=SCHEMA)

        call_action('resource_validation_run', resource_id=resource['id'])

    def test_resource_validation_with_upload(self, mocked_responses,
                                             resource_factory):
        resource = resource_factory()

        call_action('resource_validation_run', resource_id=resource['id'])

    def test_resource_validation_creates_validation_object(
            self, resource_factory):
        resource = resource_factory()

        call_action('resource_validation_run', resource_id=resource['id'])

        validation = Session.query(Validation).filter(
            Validation.resource_id == resource['id']).one()

        assert validation.resource_id == resource['id']
        assert validation.status == 'created'
        assert validation.created
        assert validation.finished is None
        assert validation.report is None
        assert validation.error is None

    def test_resource_validation_resets_existing_validation_object(
            self, mocked_responses):
        url = 'https://some.url'
        mocked_responses.add(responses.GET, url, body=VALID_CSV, stream=True)

        resource = {'format': 'csv', 'url': url, 'schema': SCHEMA}

        dataset = factories.Dataset(resources=[resource])

        timestamp = datetime.datetime.utcnow()
        old_validation = Validation(resource_id=dataset['resources'][0]['id'],
                                    created=timestamp,
                                    finished=timestamp,
                                    status='valid',
                                    report={'some': 'report'},
                                    error={'some': 'error'})

        Session.add(old_validation)
        Session.commit()

        call_action('resource_validation_run',
                    resource_id=dataset['resources'][0]['id'])

        validation = Session.query(Validation).filter(
            Validation.resource_id == dataset['resources'][0]['id']).one()

        assert validation.resource_id == dataset['resources'][0]['id']
        assert validation.status == 'created'
        assert validation.created is not timestamp
        assert validation.finished is None
        assert validation.report is None
        assert validation.error is None


@pytest.mark.usefixtures("clean_db", "validation_setup")
class TestResourceValidationShow(object):

    def test_resource_validation_show_param_missing(self):
        with pytest.raises(tk.ValidationError) as err:
            call_action('resource_validation_show')

        assert err.value.error_dict == {'resource_id': 'Missing value'}

    def test_resource_validation_show_not_exists(self):
        with pytest.raises(tk.ObjectNotFound):
            call_action('resource_validation_show', resource_id='not_exists')

    def test_resource_validation_show_validation_does_not_exists(self):

        resource = {'url': 'https://some.url'}

        dataset = factories.Dataset(resources=[resource])

        with pytest.raises(tk.ObjectNotFound) as err:
            call_action('resource_validation_show',
                        resource_id=dataset['resources'][0]['id'])

        assert 'No validation report exists for this resource' ==\
               err.value.message

    def test_resource_validation_show_returns_all_fields(self):
        resource = {'url': 'https://some.url'}

        dataset = factories.Dataset(resources=[resource])

        timestamp = datetime.datetime.utcnow()
        validation = Validation(resource_id=dataset['resources'][0]['id'],
                                created=timestamp,
                                finished=timestamp,
                                status='valid',
                                report={'some': 'report'},
                                error={'some': 'error'})
        Session.add(validation)
        Session.commit()

        validation_show = call_action(
            'resource_validation_show',
            resource_id=dataset['resources'][0]['id'])

        assert validation_show['id'] == validation.id
        assert validation_show['resource_id'] == validation.resource_id
        assert validation_show['status'] == validation.status
        assert validation_show['report'] == validation.report
        assert validation_show['error'] == validation.error
        assert validation_show['created'] == validation.created.isoformat()
        assert validation_show['finished'] == validation.finished.isoformat()


@pytest.mark.usefixtures("clean_db", "validation_setup")
class TestResourceValidationDelete(object):

    def test_resource_validation_delete_param_missing(self):
        with pytest.raises(tk.ValidationError) as err:
            call_action('resource_validation_delete')

        assert err.value.error_dict == {'resource_id': 'Missing value'}

    def test_resource_validation_delete_not_exists(self):
        with pytest.raises(tk.ObjectNotFound) as err:
            call_action('resource_validation_delete', resource_id='not_exists')

        assert 'No validation report exists for this resource' ==\
            err.value.message

    def test_resource_validation_delete_removes_object(self, resource_factory):
        resource = resource_factory(format="PDF")

        timestamp = datetime.datetime.utcnow()
        validation = Validation(resource_id=resource['id'],
                                created=timestamp,
                                finished=timestamp,
                                status='valid',
                                report={'some': 'report'},
                                error={'some': 'error'})
        Session.add(validation)
        Session.commit()

        count_before = Session.query(Validation).filter(
            Validation.resource_id == resource['id']).count()

        assert count_before == 1

        call_action('resource_validation_delete', resource_id=resource['id'])

        count_after = Session.query(Validation).filter(
            Validation.resource_id == resource['id']).count()

        assert count_after == 0


@pytest.mark.usefixtures("clean_db", "validation_setup")
class TestResourceValidationOnCreate(object):

    def test_validation_fails_on_upload(self):
        """We shouldn't be able to create a resource with an invalid file"""
        mock_upload = MockFileStorage(io.BytesIO(INVALID_CSV), 'invalid.csv')

        dataset = factories.Dataset()

        with pytest.raises(tk.ValidationError) as e:
            call_action('resource_create',
                        package_id=dataset['id'],
                        format='csv',
                        upload=mock_upload,
                        url_type='upload',
                        schema=SCHEMA)

        assert 'validation' in e.value.error_dict
        assert 'missing-cell' in str(e.value)
        assert 'Row at position "2" has a missing cell in field "d" at position "4"' in str(e.value)

    def test_validation_fails_no_validation_object_stored(self):
        """If the validation failed - no validation entity should be saved in database"""
        dataset = factories.Dataset()

        mock_upload = MockFileStorage(io.BytesIO(INVALID_CSV), 'invalid.csv')

        with pytest.raises(tk.ValidationError):
            call_action('resource_create',
                        package_id=dataset['id'],
                        format='csv',
                        upload=mock_upload,
                        url_type='upload',
                        schema=SCHEMA)

        assert not Session.query(Validation).count()

    def test_validation_skips_no_schema_provided(self):
        """If the schema is missed - no validation entity should be saved in database"""
        dataset = factories.Dataset()

        mock_upload = MockFileStorage(io.BytesIO(VALID_CSV), 'valid.csv')

        call_action('resource_create',
                    package_id=dataset['id'],
                    format='csv',
                    upload=mock_upload,
                    url_type='upload')

        assert not Session.query(Validation).count()

    def test_validation_report_delete_when_schema_removed(self):
        """If the schema is deleted - no validation entity should be saved in database"""
        dataset = factories.Dataset()

        mock_upload = MockFileStorage(io.BytesIO(VALID_CSV), 'valid.csv')

        resource_1 = call_action('resource_create',
                                 package_id=dataset['id'],
                                 format='csv',
                                 upload=mock_upload,
                                 url_type='upload',
                                 schema=SCHEMA)

        assert Session.query(Validation).count()

        call_action('resource_patch',
                    id=resource_1['id'],
                    schema='')

        assert not Session.query(Validation).count()

    def test_validation_passes_on_upload(self):
        dataset = factories.Dataset()

        mock_upload = MockFileStorage(io.BytesIO(VALID_CSV), 'valid.csv')

        resource = call_action('resource_create',
                               package_id=dataset['id'],
                               format='csv',
                               upload=mock_upload,
                               url_type='upload',
                               schema=SCHEMA)

        assert resource['validation_status'] == 'success'
        assert 'validation_timestamp' in resource

    def test_validation_passes_on_upload_with_latin_encoding(self):
        dataset = factories.Dataset()

        mock_upload = MockFileStorage(io.BytesIO(LATIN1_CSV), 'latin1.csv')

        resource = call_action('resource_create',
                               package_id=dataset['id'],
                               format='csv',
                               upload=mock_upload,
                               url_type='upload',
                               schema=SCHEMA)

        assert resource['validation_status'] == 'success'
        assert 'validation_timestamp' in resource

    def test_validation_passes_with_url(self, mocked_responses):
        dataset = factories.Dataset()

        url = 'https://example.com/valid.csv'
        mocked_responses.add(responses.GET, url, body=VALID_CSV, stream=True)

        resource = call_action('resource_create',
                               package_id=dataset['id'],
                               format='csv',
                               url=url,
                               schema=SCHEMA)

        assert resource['validation_status'] == 'success'
        assert 'validation_timestamp' in resource

    def test_validation_fails_if_schema_invalid(self, resource_factory):
        with pytest.raises(tk.ValidationError, match="Schema is invalid"):
            resource_factory(schema="{111}")


@pytest.mark.usefixtures("clean_db", "validation_setup")
class TestResourceValidationOnUpdate(object):

    def test_validation_fails_on_upload(self, resource_factory):
        dataset = factories.Dataset()
        resource = resource_factory(package_id=dataset["id"], schema="")

        mock_upload = MockFileStorage(io.BytesIO(INVALID_CSV), 'invalid.csv')

        with pytest.raises(tk.ValidationError) as e:
            call_action('resource_update',
                        id=resource['id'],
                        package_id=dataset['id'],
                        upload=mock_upload,
                        format='csv',
                        schema=SCHEMA)

        assert 'validation' in e.value.error_dict
        assert 'missing-cell' in str(e.value)
        assert 'Row at position "2" has a missing cell in field "d" at position "4"' in str(e.value)

    def test_validation_fails_no_validation_object_stored(
            self, resource_factory):
        dataset = factories.Dataset()

        mock_upload = MockFileStorage(six.BytesIO(INVALID_CSV), 'valid.csv')

        with pytest.raises(tk.ValidationError):
            resource_factory(package_id=dataset['id'], upload=mock_upload)

        assert Session.query(Validation).count() == 0

    def test_validation_passes_on_upload(self, resource_factory):
        dataset = factories.Dataset()
        resource = resource_factory(package_id=dataset["id"], format="")

        assert 'validation_status' not in resource

        mock_upload = MockFileStorage(six.BytesIO(VALID_CSV), 'valid.csv')

        resource = call_action('resource_update',
                               id=resource['id'],
                               package_id=dataset['id'],
                               format='csv',
                               upload=mock_upload,
                               schema=SCHEMA)

        assert resource['validation_status'] == 'success'
        assert 'validation_timestamp' in resource

    def test_validation_passes_with_url(self, mocked_responses,
                                        resource_factory):
        dataset = factories.Dataset()
        resource = resource_factory(package_id=dataset["id"], format="")

        assert 'validation_status' not in resource

        url = 'https://example.com/data.csv'
        mocked_responses.add(responses.GET, url, body=VALID_CSV, stream=True)

        resource = call_action('resource_update',
                               id=resource['id'],
                               package_id=dataset["id"],
                               format='csv',
                               url=url,
                               schema=SCHEMA)

        assert resource['validation_status'] == 'success'
        assert 'validation_timestamp' in resource

    def test_validation_passes_with_schema_as_url(self, mocked_responses,
                                                  resource_factory):
        schema_url = 'https://example.com/schema.json'

        mocked_responses.add(responses.GET, schema_url, json=SCHEMA)

        resource = resource_factory(schema=schema_url)

        assert resource['schema'] == schema_url
        assert resource['validation_status'] == 'success'
        assert 'validation_timestamp' in resource

    def test_validation_fails_if_schema_invalid(self, resource_factory):
        resource = resource_factory(format="pdf")
        with pytest.raises(tk.ValidationError, match="Schema is invalid"):
            call_action('resource_update',
                        id=resource['id'],
                        package_id=resource['package_id'],
                        format='csv',
                        schema="{111}")


@pytest.mark.usefixtures("clean_db", "validation_setup")
@mock.patch('ckanext.validation.jobs.validate', return_value=VALID_REPORT)
class TestSchemaFields(object):

    def test_schema_field(self, mocked_report):
        dataset = factories.Dataset()

        resource = call_action('resource_create',
                               package_id=dataset['id'],
                               url='http://example.com/file.csv',
                               schema=json.dumps(SCHEMA))

        assert resource['schema'] == SCHEMA
        assert 'schema_upload' not in resource
        assert 'schema_url' not in resource

    def test_schema_url_field(self, mocked_report, mocked_responses):
        schema_url = 'https://example.com/schema.json'
        mocked_responses.add(responses.GET, schema_url, json=SCHEMA)

        dataset = factories.Dataset()

        resource = call_action('resource_create',
                               package_id=dataset['id'],
                               url='http://example.com/file.csv',
                               schema_url=schema_url)

        assert resource['schema'] == SCHEMA
        assert 'schema_upload' not in resource
        assert 'schema_url' not in resource

    def test_schema_url_field_wrong_url(self, mocked_report):
        with pytest.raises(tk.ValidationError):
            call_action('resource_create',
                        url='http://example.com/file.csv',
                        schema_url='not-a-url')

    def test_schema_upload_field(self, mocked_report):
        schema_upload = MockFileStorage(
            six.BytesIO(six.ensure_binary(json.dumps(SCHEMA))), 'schema.json')

        dataset = factories.Dataset()

        resource = call_action('resource_create',
                               package_id=dataset['id'],
                               url='http://example.com/file.csv',
                               schema_upload=schema_upload)

        assert resource['schema'] == SCHEMA
        assert 'schema_upload' not in resource
        assert 'schema_url' not in resource


@pytest.mark.usefixtures("clean_db", "validation_setup")
@mock.patch('ckanext.validation.jobs.validate', return_value=VALID_REPORT)
class TestValidationOptionsField(object):

    def test_validation_options_field(self, mocked_report):
        dataset = factories.Dataset()

        validation_options = {
            'delimiter': ';',
            'headers': 2,
            'skip_rows': ['#'],
        }

        resource = call_action(
            'resource_create',
            package_id=dataset['id'],
            url='http://example.com/file.csv',
            validation_options=validation_options,
        )

        assert resource['validation_options'] == validation_options

    def test_validation_options_field_string(self, mocked_report):
        dataset = factories.Dataset()

        validation_options = '''{
            "delimiter": ";",
            "headers": 2,
            "skip_rows": ["#"]
        }'''

        resource = call_action(
            'resource_create',
            package_id=dataset['id'],
            url='http://example.com/file.csv',
            validation_options=validation_options,
        )

        assert resource['validation_options'] == json.loads(validation_options)


@pytest.mark.usefixtures("clean_db", "validation_setup")
class TestPackageUpdate(object):

    def test_package_patch_without_resources_sets_context_flag(self):
        dataset = factories.Dataset()
        context = {}
        call_action('package_patch', context=context, id=dataset['id'])
        assert context.get('save', False)

    def test_package_patch_with_resources_does_not_set_context_flag(self):
        dataset = factories.Dataset()
        context = {}
        call_action('package_patch',
                    context=context,
                    id=dataset['id'],
                    resources=[])
        assert 'save' not in context


@pytest.mark.usefixtures("clean_db", "validation_setup")
class TestAuth(object):

    @pytest.mark.ckan_config("ckanext.validation.run_on_create_sync", False)
    @pytest.mark.ckan_config("ckanext.validation.run_on_update_sync", False)
    def test_run_anon(self):
        resource = factories.Resource()
        context = {'user': None, 'model': model}

        with pytest.raises(tk.NotAuthorized):
            call_auth('resource_validation_run',
                      context=context,
                      resource_id=resource['id'])

    @pytest.mark.ckan_config("ckanext.validation.run_on_create_sync", False)
    @pytest.mark.ckan_config("ckanext.validation.run_on_update_sync", False)
    def test_run_sysadmin(self):
        resource = factories.Resource()
        sysadmin = factories.Sysadmin()
        context = {'user': sysadmin['name'], 'model': model}

        assert call_auth('resource_validation_run',
                         context=context,
                         resource_id=resource['id'])

    @pytest.mark.ckan_config("ckanext.validation.run_on_create_sync", False)
    @pytest.mark.ckan_config("ckanext.validation.run_on_update_sync", False)
    def test_run_non_auth_user(self):
        user = factories.User()
        org = factories.Organization()
        dataset = factories.Dataset(owner_org=org['id'])
        resource = factories.Resource(package_id=dataset["id"])
        context = {'user': user['name'], 'model': model}

        with pytest.raises(tk.NotAuthorized):
            call_auth('resource_validation_run',
                      context=context,
                      resource_id=resource['id'])

    @pytest.mark.ckan_config("ckanext.validation.run_on_create_sync", False)
    @pytest.mark.ckan_config("ckanext.validation.run_on_update_sync", False)
    def test_run_auth_user(self):
        user = factories.User()
        org = factories.Organization(users=[{
            'name': user['name'],
            'capacity': 'editor'
        }])
        dataset = factories.Dataset(owner_org=org['id'])
        resource = factories.Resource(package_id=dataset["id"])
        context = {'user': user['name'], 'model': model}

        assert call_auth('resource_validation_run',
                         context=context,
                         resource_id=resource['id'])

    @pytest.mark.ckan_config("ckanext.validation.run_on_create_sync", False)
    @pytest.mark.ckan_config("ckanext.validation.run_on_update_sync", False)
    def test_delete_anon(self):
        resource = factories.Resource()
        context = {'user': None, 'model': model}

        with pytest.raises(tk.NotAuthorized):
            call_auth('resource_validation_delete',
                      context=context,
                      resource_id=resource['id'])

    @pytest.mark.ckan_config("ckanext.validation.run_on_create_sync", False)
    @pytest.mark.ckan_config("ckanext.validation.run_on_update_sync", False)
    def test_delete_sysadmin(self):
        resource = factories.Resource()
        sysadmin = factories.Sysadmin()
        context = {'user': sysadmin['name'], 'model': model}

        assert call_auth('resource_validation_delete',
                         context=context,
                         resource_id=resource['id'])

    @pytest.mark.ckan_config("ckanext.validation.run_on_create_sync", False)
    @pytest.mark.ckan_config("ckanext.validation.run_on_update_sync", False)
    def test_delete_non_auth_user(self):
        user = factories.User()
        org = factories.Organization()
        dataset = factories.Dataset(owner_org=org['id'])
        resource = factories.Resource(package_id=dataset["id"])

        context = {'user': user['name'], 'model': model}

        with pytest.raises(tk.NotAuthorized):
            call_auth('resource_validation_delete',
                      context=context,
                      resource_id=resource['id'])

    @pytest.mark.ckan_config("ckanext.validation.run_on_create_sync", False)
    @pytest.mark.ckan_config("ckanext.validation.run_on_update_sync", False)
    def test_delete_auth_user(self):
        user = factories.User()
        org = factories.Organization(users=[{
            'name': user['name'],
            'capacity': 'editor'
        }])
        dataset = factories.Dataset(owner_org=org['id'])
        resource = factories.Resource(package_id=dataset["id"])
        context = {'user': user['name'], 'model': model}

        assert call_auth('resource_validation_delete',
                         context=context,
                         resource_id=resource['id'])

    @pytest.mark.ckan_config("ckanext.validation.run_on_create_sync", False)
    @pytest.mark.ckan_config("ckanext.validation.run_on_update_sync", False)
    def test_show_anon(self):
        resource = factories.Resource()
        context = {'user': None, 'model': model}

        assert call_auth('resource_validation_show',
                         context=context,
                         resource_id=resource['id'])

    @pytest.mark.ckan_config("ckanext.validation.run_on_create_sync", False)
    @pytest.mark.ckan_config("ckanext.validation.run_on_update_sync", False)
    def test_show_anon_public_dataset(self):
        user = factories.User()
        org = factories.Organization()
        dataset = factories.Dataset(owner_org=org['id'],
                                    private=False)
        resource = factories.Resource(package_id=dataset["id"])
        context = {'user': user['name'], 'model': model}

        assert call_auth('resource_validation_show',
                         context=context,
                         resource_id=resource['id'])

    @pytest.mark.ckan_config("ckanext.validation.run_on_create_sync", False)
    @pytest.mark.ckan_config("ckanext.validation.run_on_update_sync", False)
    def test_show_anon_private_dataset(self):
        user = factories.User()
        org = factories.Organization()
        dataset = factories.Dataset(owner_org=org['id'],
                                    private=True)
        resource = factories.Resource(package_id=dataset["id"])
        context = {'user': user['name'], 'model': model}

        with pytest.raises(tk.NotAuthorized):
            call_auth('resource_validation_run',
                      context=context,
                      resource_id=resource['id'])
