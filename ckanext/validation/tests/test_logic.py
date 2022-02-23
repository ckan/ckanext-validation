import datetime
import StringIO
import io
import json

from nose.tools import assert_raises, assert_equals
import mock

from ckan import model
from ckan.tests.helpers import (
    call_action, call_auth, change_config, reset_db, FunctionalTestBase
)
from ckan.tests import factories

import ckantoolkit as t

from ckanext.validation.model import create_tables, tables_exist, Validation
from ckanext.validation.tests.helpers import (
    VALID_CSV, INVALID_CSV, VALID_REPORT,
    mock_uploads, MockFieldStorage
)


Session = model.Session


class TestResourceValidationRun(object):

    def setup(self):

        # We don't use FunctionalTestBase here as we need to change the config
        # in individual tests

        reset_db()

        if not tables_exist():
            create_tables()

    def test_resource_validation_run_param_missing(self):

        assert_raises(
            t.ValidationError,
            call_action, 'resource_validation_run')

    def test_resource_validation_run_not_exists(self):

        assert_raises(
            t.ObjectNotFound,
            call_action, 'resource_validation_run', resource_id='not_exists')

    def test_resource_validation_wrong_format(self):

        resource = factories.Resource(format='pdf')

        with assert_raises(t.ValidationError) as e:

            call_action('resource_validation_run', resource_id=resource['id'])

        assert 'Unsupported resource format' in str(e.exception)

    def test_resource_validation_no_url_or_upload(self):

        resource = factories.Resource(url='', format='csv')

        with assert_raises(t.ValidationError) as e:

            call_action('resource_validation_run', resource_id=resource['id'])

        assert 'Resource must have a valid URL' in str(e.exception)

    @mock.patch('ckanext.validation.logic.enqueue_job')
    def test_resource_validation_with_url(self, mock_enqueue_job):

        resource = factories.Resource(url='http://example.com', format='csv')

        call_action('resource_validation_run', resource_id=resource['id'])

    @mock.patch('ckanext.validation.logic.enqueue_job')
    def test_resource_validation_with_upload(self, mock_enqueue_job):

        resource = factories.Resource(url='', url_type='upload', format='csv')

        call_action('resource_validation_run', resource_id=resource['id'])

    def test_resource_validation_run_starts_job(self):

        resource = factories.Resource(format='csv')

        jobs = call_action('job_list')

        call_action('resource_validation_run', resource_id=resource['id'])

        jobs_after = call_action('job_list')

        assert len(jobs_after) == len(jobs) + 1

    @mock.patch('ckanext.validation.logic.enqueue_job')
    def test_resource_validation_creates_validation_object(
            self, mock_enqueue_job):

        resource = factories.Resource(format='csv')

        call_action('resource_validation_run', resource_id=resource['id'])

        validation = Session.query(Validation).filter(
            Validation.resource_id == resource['id']).one()

        assert_equals(validation.resource_id, resource['id'])
        assert_equals(validation.status, 'created')
        assert validation.created
        assert_equals(validation.finished, None)
        assert_equals(validation.report, None)
        assert_equals(validation.error, None)

    @change_config('ckanext.validation.run_on_create_async', False)
    @mock.patch('ckanext.validation.logic.enqueue_job')
    def test_resource_validation_resets_existing_validation_object(
            self, mock_enqueue_job):

        resource = {'format': 'CSV', 'url': 'https://some.url'}

        dataset = factories.Dataset(resources=[resource])

        timestamp = datetime.datetime.utcnow()
        old_validation = Validation(
            resource_id=dataset['resources'][0]['id'],
            created=timestamp,
            finished=timestamp,
            status='valid',
            report={'some': 'report'},
            error={'some': 'error'})

        Session.add(old_validation)
        Session.commit()

        call_action(
            'resource_validation_run',
            resource_id=dataset['resources'][0]['id']
        )

        validation = Session.query(Validation).filter(
            Validation.resource_id == dataset['resources'][0]['id']).one()

        assert_equals(validation.resource_id, dataset['resources'][0]['id'])
        assert_equals(validation.status, 'created')
        assert validation.created is not timestamp
        assert_equals(validation.finished, None)
        assert_equals(validation.report, None)
        assert_equals(validation.error, None)


class TestResourceValidationShow(FunctionalTestBase):

    def setup(self):

        super(TestResourceValidationShow, self).setup()

        if not tables_exist():
            create_tables()

    def test_resource_validation_show_param_missing(self):

        assert_raises(
            t.ValidationError,
            call_action, 'resource_validation_show')

    def test_resource_validation_show_not_exists(self):

        assert_raises(
            t.ObjectNotFound,
            call_action, 'resource_validation_show', resource_id='not_exists')

    @change_config('ckanext.validation.run_on_create_async', False)
    def test_resource_validation_show_validation_does_not_exists(self):

        resource = {'format': 'CSV', 'url': 'https://some.url'}

        dataset = factories.Dataset(resources=[resource])

        assert_raises(
            t.ObjectNotFound,
            call_action, 'resource_validation_show',
            resource_id=dataset['resources'][0]['id'])

    @change_config('ckanext.validation.run_on_create_async', False)
    def test_resource_validation_show_returns_all_fields(self):

        resource = {'format': 'CSV', 'url': 'https://some.url'}

        dataset = factories.Dataset(resources=[resource])

        timestamp = datetime.datetime.utcnow()
        validation = Validation(
            resource_id=dataset['resources'][0]['id'],
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

        assert_equals(validation_show['id'], validation.id)
        assert_equals(validation_show['resource_id'], validation.resource_id)
        assert_equals(validation_show['status'], validation.status)
        assert_equals(validation_show['report'], validation.report)
        assert_equals(validation_show['error'], validation.error)
        assert_equals(
            validation_show['created'], validation.created.isoformat())
        assert_equals(
            validation_show['finished'], validation.finished.isoformat())


class TestResourceValidationDelete(FunctionalTestBase):

    def setup(self):

        super(TestResourceValidationDelete, self).setup()

        if not tables_exist():
            create_tables()

    def test_resource_validation_delete_param_missing(self):

        assert_raises(
            t.ValidationError,
            call_action, 'resource_validation_delete')

    def test_resource_validation_delete_not_exists(self):

        assert_raises(
            t.ObjectNotFound,
            call_action, 'resource_validation_delete',
            resource_id='not_exists')

    @change_config('ckanext.validation.run_on_create_async', False)
    @change_config('ckanext.validation.run_on_update_async', False)
    def test_resource_validation_delete_removes_object(self):

        resource = factories.Resource(format='csv')
        timestamp = datetime.datetime.utcnow()
        validation = Validation(
            resource_id=resource['id'],
            created=timestamp,
            finished=timestamp,
            status='valid',
            report={'some': 'report'},
            error={'some': 'error'})
        Session.add(validation)
        Session.commit()

        count_before = Session.query(Validation).filter(
            Validation.resource_id == resource['id']).count()

        assert_equals(count_before, 1)

        call_action('resource_validation_delete', resource_id=resource['id'])

        count_after = Session.query(Validation).filter(
            Validation.resource_id == resource['id']).count()

        assert_equals(count_after, 0)


class TestAuth(FunctionalTestBase):

    def setup(self):

        super(TestAuth, self).setup()

        if not tables_exist():
            create_tables()

    def test_run_anon(self):

        resource = factories.Resource()

        context = {
            'user': None,
            'model': model
        }

        assert_raises(t.NotAuthorized,
                      call_auth, 'resource_validation_run', context=context,
                      resource_id=resource['id'])

    def test_run_sysadmin(self):

        resource = factories.Resource()
        sysadmin = factories.Sysadmin()

        context = {
            'user': sysadmin['name'],
            'model': model
        }

        assert_equals(call_auth('resource_validation_run', context=context,
                                resource_id=resource['id']),
                      True)

    def test_run_non_auth_user(self):

        user = factories.User()
        org = factories.Organization()
        dataset = factories.Dataset(
            owner_org=org['id'], resources=[factories.Resource()])

        context = {
            'user': user['name'],
            'model': model
        }

        assert_raises(t.NotAuthorized,
                      call_auth, 'resource_validation_run', context=context,
                      resource_id=dataset['resources'][0]['id'])

    def test_run_auth_user(self):

        user = factories.User()
        org = factories.Organization(
            users=[{'name': user['name'], 'capacity': 'editor'}])
        dataset = factories.Dataset(
            owner_org=org['id'], resources=[factories.Resource()])

        context = {
            'user': user['name'],
            'model': model
        }

        assert_equals(call_auth('resource_validation_run', context=context,
                                resource_id=dataset['resources'][0]['id']),
                      True)

    def test_delete_anon(self):

        resource = factories.Resource()

        context = {
            'user': None,
            'model': model
        }

        assert_raises(t.NotAuthorized,
                      call_auth, 'resource_validation_delete', context=context,
                      resource_id=resource['id'])

    def test_delete_sysadmin(self):

        resource = factories.Resource()
        sysadmin = factories.Sysadmin()

        context = {
            'user': sysadmin['name'],
            'model': model
        }

        assert_equals(call_auth('resource_validation_delete', context=context,
                                resource_id=resource['id']),
                      True)

    def test_delete_non_auth_user(self):

        user = factories.User()
        org = factories.Organization()
        dataset = factories.Dataset(
            owner_org=org['id'], resources=[factories.Resource()])

        context = {
            'user': user['name'],
            'model': model
        }

        assert_raises(t.NotAuthorized,
                      call_auth, 'resource_validation_delete', context=context,
                      resource_id=dataset['resources'][0]['id'])

    def test_delete_auth_user(self):

        user = factories.User()
        org = factories.Organization(
            users=[{'name': user['name'], 'capacity': 'editor'}])
        dataset = factories.Dataset(
            owner_org=org['id'], resources=[factories.Resource()])

        context = {
            'user': user['name'],
            'model': model
        }

        assert_equals(call_auth('resource_validation_delete', context=context,
                                resource_id=dataset['resources'][0]['id']),
                      True)

    def test_show_anon(self):

        resource = factories.Resource()

        context = {
            'user': None,
            'model': model
        }

        assert_equals(call_auth('resource_validation_show', context=context,
                                resource_id=resource['id']),
                      True)

    def test_show_anon_public_dataset(self):

        user = factories.User()
        org = factories.Organization()
        dataset = factories.Dataset(
            owner_org=org['id'], resources=[factories.Resource()],
            private=False)

        context = {
            'user': user['name'],
            'model': model
        }

        assert_equals(call_auth('resource_validation_show', context=context,
                                resource_id=dataset['resources'][0]['id']),
                      True)

    def test_show_anon_private_dataset(self):

        user = factories.User()
        org = factories.Organization()
        dataset = factories.Dataset(
            owner_org=org['id'], resources=[factories.Resource()],
            private=True)

        context = {
            'user': user['name'],
            'model': model
        }

        assert_raises(t.NotAuthorized,
                      call_auth, 'resource_validation_run', context=context,
                      resource_id=dataset['resources'][0]['id'])


class TestResourceValidationOnCreate(FunctionalTestBase):

    @classmethod
    def _apply_config_changes(cls, cfg):
        cfg['ckanext.validation.run_on_create_sync'] = True

    def setup(self):

        super(TestResourceValidationOnCreate, self).setup()

        if not tables_exist():
            create_tables()

    @mock_uploads
    def test_validation_fails_on_upload(self, mock_open):

        invalid_file = StringIO.StringIO()
        invalid_file.write(INVALID_CSV)

        mock_upload = MockFieldStorage(invalid_file, 'invalid.csv')

        dataset = factories.Dataset()

        invalid_stream = io.BufferedReader(io.BytesIO(INVALID_CSV))

        with mock.patch('io.open', return_value=invalid_stream):

            with assert_raises(t.ValidationError) as e:

                call_action(
                    'resource_create',
                    package_id=dataset['id'],
                    format='CSV',
                    upload=mock_upload
                )

        assert 'validation' in e.exception.error_dict
        assert 'missing-value' in str(e.exception)
        assert 'Row 2 has a missing value in column 4' in str(e.exception)

    @mock_uploads
    def test_validation_fails_no_validation_object_stored(self, mock_open):

        invalid_file = StringIO.StringIO()
        invalid_file.write(INVALID_CSV)

        mock_upload = MockFieldStorage(invalid_file, 'invalid.csv')

        dataset = factories.Dataset()

        invalid_stream = io.BufferedReader(io.BytesIO(INVALID_CSV))

        validation_count_before = model.Session.query(Validation).count()

        with mock.patch('io.open', return_value=invalid_stream):

            with assert_raises(t.ValidationError):
                call_action(
                    'resource_create',
                    package_id=dataset['id'],
                    format='CSV',
                    upload=mock_upload
                )

        validation_count_after = model.Session.query(Validation).count()

        assert_equals(validation_count_after, validation_count_before)

    @mock_uploads
    def test_validation_passes_on_upload(self, mock_open):

        invalid_file = StringIO.StringIO()
        invalid_file.write(VALID_CSV)

        mock_upload = MockFieldStorage(invalid_file, 'invalid.csv')

        dataset = factories.Dataset()

        valid_stream = io.BufferedReader(io.BytesIO(VALID_CSV))

        with mock.patch('io.open', return_value=valid_stream):

            resource = call_action(
                'resource_create',
                package_id=dataset['id'],
                format='CSV',
                upload=mock_upload
            )

        assert_equals(resource['validation_status'], 'success')
        assert 'validation_timestamp' in resource

    @mock.patch('ckanext.validation.jobs.validate',
                return_value=VALID_REPORT)
    def test_validation_passes_with_url(self, mock_validate):

        url = 'https://example.com/valid.csv'

        dataset = factories.Dataset()

        resource = call_action(
            'resource_create',
            package_id=dataset['id'],
            format='csv',
            url=url,
        )

        assert_equals(resource['validation_status'], 'success')
        assert 'validation_timestamp' in resource


class TestResourceValidationOnUpdate(FunctionalTestBase):

    @classmethod
    def _apply_config_changes(cls, cfg):
        cfg['ckanext.validation.run_on_update_sync'] = True

    def setup(self):

        super(TestResourceValidationOnUpdate, self).setup()

        if not tables_exist():
            create_tables()

    @mock_uploads
    def test_validation_fails_on_upload(self, mock_open):

        dataset = factories.Dataset(resources=[
            {
                'url': 'https://example.com/data.csv'
            }
        ])

        invalid_file = StringIO.StringIO()
        invalid_file.write(INVALID_CSV)

        mock_upload = MockFieldStorage(invalid_file, 'invalid.csv')

        invalid_stream = io.BufferedReader(io.BytesIO(INVALID_CSV))

        with mock.patch('io.open', return_value=invalid_stream):

            with assert_raises(t.ValidationError) as e:

                call_action(
                    'resource_update',
                    id=dataset['resources'][0]['id'],
                    format='CSV',
                    upload=mock_upload
                )

        assert 'validation' in e.exception.error_dict
        assert 'missing-value' in str(e.exception)
        assert 'Row 2 has a missing value in column 4' in str(e.exception)

    @mock_uploads
    def test_validation_fails_no_validation_object_stored(self, mock_open):

        dataset = factories.Dataset(resources=[
            {
                'url': 'https://example.com/data.csv'
            }
        ])

        invalid_file = StringIO.StringIO()
        invalid_file.write(INVALID_CSV)

        mock_upload = MockFieldStorage(invalid_file, 'invalid.csv')

        invalid_stream = io.BufferedReader(io.BytesIO(INVALID_CSV))

        with mock.patch('io.open', return_value=invalid_stream):

            with assert_raises(t.ValidationError):

                call_action(
                    'resource_update',
                    id=dataset['resources'][0]['id'],
                    format='CSV',
                    upload=mock_upload
                )

        validation_count_after = model.Session.query(Validation).count()

        assert_equals(validation_count_after, 0)

    @mock_uploads
    def test_validation_passes_on_upload(self, mock_open):

        dataset = factories.Dataset(resources=[
            {
                'url': 'https://example.com/data.csv'
            }
        ])

        valid_file = StringIO.StringIO()
        valid_file.write(INVALID_CSV)

        mock_upload = MockFieldStorage(valid_file, 'valid.csv')

        valid_stream = io.BufferedReader(io.BytesIO(VALID_CSV))

        with mock.patch('io.open', return_value=valid_stream):

            resource = call_action(
                'resource_update',
                id=dataset['resources'][0]['id'],
                format='CSV',
                upload=mock_upload
            )

        assert_equals(resource['validation_status'], 'success')
        assert 'validation_timestamp' in resource

    @mock.patch('ckanext.validation.jobs.validate',
                return_value=VALID_REPORT)
    def test_validation_passes_with_url(self, mock_validate):

        dataset = factories.Dataset(resources=[
            {
                'url': 'https://example.com/data.csv'
            }
        ])

        resource = call_action(
            'resource_update',
            id=dataset['resources'][0]['id'],
            format='CSV',
            url='https://example.com/some.other.csv',
        )

        assert_equals(resource['validation_status'], 'success')
        assert 'validation_timestamp' in resource


class TestSchemaFields(FunctionalTestBase):

    def setup(self):

        super(TestSchemaFields, self).setup()

        if not tables_exist():
            create_tables()

    def test_schema_field(self):

        dataset = factories.Dataset()

        resource = call_action(
            'resource_create',
            package_id=dataset['id'],
            url='http://example.com/file.csv',
            schema='{"fields":[{"name":"id"}]}'
        )

        assert_equals(resource['schema'], {'fields': [{'name': 'id'}]})

        assert 'schema_upload' not in resource
        assert 'schema_url' not in resource

    def test_schema_field_url(self):

        url = 'https://example.com/schema.json'

        dataset = factories.Dataset()

        resource = call_action(
            'resource_create',
            package_id=dataset['id'],
            url='http://example.com/file.csv',
            schema=url
        )

        assert_equals(resource['schema'], url)

        assert 'schema_upload' not in resource
        assert 'schema_url' not in resource

    def test_schema_url_field(self):

        url = 'https://example.com/schema.json'

        dataset = factories.Dataset()

        resource = call_action(
            'resource_create',
            package_id=dataset['id'],
            url='http://example.com/file.csv',
            schema_url=url
        )

        assert_equals(resource['schema'], url)

        assert 'schema_upload' not in resource
        assert 'schema_url' not in resource

    def test_schema_url_field_wrong_url(self):

        url = 'not-a-url'

        assert_raises(
            t.ValidationError, call_action, 'resource_create',
            url='http://example.com/file.csv',
            schema_url=url
        )

    @mock_uploads
    def test_schema_upload_field(self, mock_open):

        schema_file = StringIO.StringIO('{"fields":[{"name":"category"}]}')

        mock_upload = MockFieldStorage(schema_file, 'schema.json')

        dataset = factories.Dataset()

        resource = call_action(
            'resource_create',
            package_id=dataset['id'],
            url='http://example.com/file.csv',
            schema_upload=mock_upload
        )

        assert_equals(resource['schema'], {'fields': [{'name': 'category'}]})

        assert 'schema_upload' not in resource
        assert 'schema_url' not in resource


class TestValidationOptionsField(FunctionalTestBase):

    def setup(self):

        super(TestValidationOptionsField, self).setup()

        if not tables_exist():
            create_tables()

    def test_validation_options_field(self):

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

        assert_equals(resource['validation_options'], validation_options)

    def test_validation_options_field_string(self):

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

        assert_equals(resource['validation_options'],
                      json.loads(validation_options))
