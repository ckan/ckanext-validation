import mock
import StringIO
import json
import io

from nose.tools import assert_equals

import ckantoolkit

from ckan.lib.uploader import ResourceUpload
from ckan.tests.helpers import call_action, reset_db, change_config
from ckan.tests import factories

from ckanext.validation.model import create_tables, tables_exist, Validation
from ckanext.validation.jobs import (
    run_validation_job, uploader, Session)
from ckanext.validation.tests.helpers import (
    VALID_REPORT, INVALID_REPORT, ERROR_REPORT, VALID_REPORT_LOCAL_FILE,
    mock_uploads, MockFieldStorage
)


class MockUploader(ResourceUpload):

    def get_path(self, resource_id):
        return '/tmp/example/{}'.format(resource_id)


def mock_get_resource_uploader(data_dict):
    return MockUploader(data_dict)


class TestValidationJob(object):

    def setup(self):
        reset_db()
        if not tables_exist():
            create_tables()

    @change_config('ckanext.validation.run_on_create_async', False)
    @mock.patch('ckanext.validation.jobs.validate')
    @mock.patch.object(Session, 'commit')
    @mock.patch.object(ckantoolkit, 'get_action')
    def test_job_run_no_schema(self, mock_get_action, mock_commit, mock_validate):

        org = factories.Organization()
        dataset = factories.Dataset(private=True, owner_org=org['id'])

        resource = {
            'id': 'test',
            'url': 'http://example.com/file.csv',
            'format': 'csv',
            'package_id': dataset['id'],
        }

        run_validation_job(resource)

        mock_validate.assert_called_with(
            'http://example.com/file.csv',
            format='csv',
            schema=None)

    @mock.patch('ckanext.validation.jobs.validate')
    @mock.patch.object(Session, 'commit')
    @mock.patch.object(ckantoolkit, 'get_action')
    def test_job_run_schema(self, mock_get_action, mock_commit, mock_validate):

        org = factories.Organization()
        dataset = factories.Dataset(private=True, owner_org=org['id'])

        schema = {
            'fields': [
                {'name': 'id', 'type': 'integer'},
                {'name': 'description', 'type': 'string'}
            ]
        }
        resource = {
            'id': 'test',
            'url': 'http://example.com/file.csv',
            'format': 'csv',
            'schema': json.dumps(schema),
            'package_id': dataset['id'],
        }

        run_validation_job(resource)

        mock_validate.assert_called_with(
            'http://example.com/file.csv',
            format='csv',
            schema=schema)

    @mock.patch('ckanext.validation.jobs.validate')
    @mock.patch.object(uploader, 'get_resource_uploader',
                       return_value=mock_get_resource_uploader({}))
    @mock.patch.object(Session, 'commit')
    @mock.patch.object(ckantoolkit, 'get_action')
    def test_job_run_uploaded_file(
            self, mock_get_action, mock_commit, mock_uploader, mock_validate):

        org = factories.Organization()
        dataset = factories.Dataset(private=True, owner_org=org['id'])

        resource = {
            'id': 'test',
            'url': '__upload',
            'url_type': 'upload',
            'format': 'csv',
            'package_id': dataset['id'],
        }

        run_validation_job(resource)

        mock_validate.assert_called_with(
            '/tmp/example/{}'.format(resource['id']),
            format='csv',
            schema=None)

    @mock.patch('ckanext.validation.jobs.validate',
                return_value=VALID_REPORT)
    def test_job_run_valid_stores_validation_object(self, mock_validate):

        resource = factories.Resource(
            url='http://example.com/file.csv', format='csv')

        run_validation_job(resource)

        validation = Session.query(Validation).filter(
            Validation.resource_id == resource['id']).one()

        assert_equals(validation.status, 'success')
        assert_equals(validation.report, VALID_REPORT)
        assert validation.finished

    @mock.patch('ckanext.validation.jobs.validate',
                return_value=INVALID_REPORT)
    def test_job_run_invalid_stores_validation_object(self, mock_validate):

        resource = factories.Resource(
            url='http://example.com/file.csv', format='csv')

        run_validation_job(resource)

        validation = Session.query(Validation).filter(
            Validation.resource_id == resource['id']).one()

        assert_equals(validation.status, 'failure')
        assert_equals(validation.report, INVALID_REPORT)
        assert validation.finished

    @mock.patch('ckanext.validation.jobs.validate',
                return_value=ERROR_REPORT)
    def test_job_run_error_stores_validation_object(self, mock_validate):

        resource = factories.Resource(
            url='http://example.com/file.csv', format='csv')

        run_validation_job(resource)

        validation = Session.query(Validation).filter(
            Validation.resource_id == resource['id']).one()

        assert_equals(validation.status, 'error')
        assert_equals(validation.report, None)
        assert_equals(validation.error, {'message': 'Some warning'})
        assert validation.finished

    @mock.patch('ckanext.validation.jobs.validate',
                return_value=VALID_REPORT_LOCAL_FILE)
    @mock.patch.object(uploader, 'get_resource_uploader',
                       return_value=mock_get_resource_uploader({}))
    def test_job_run_uploaded_file_replaces_paths(
            self, mock_uploader, mock_validate):

        resource = factories.Resource(
            url='__upload', url_type='upload', format='csv')

        run_validation_job(resource)

        validation = Session.query(Validation).filter(
            Validation.resource_id == resource['id']).one()

        assert validation.report['tables'][0]['source'].startswith('http')

    @mock.patch('ckanext.validation.jobs.validate',
                return_value=VALID_REPORT)
    def test_job_run_valid_stores_status_in_resource(self, mock_validate):

        resource = factories.Resource(
            url='http://example.com/file.csv', format='csv')

        run_validation_job(resource)

        validation = Session.query(Validation).filter(
            Validation.resource_id == resource['id']).one()

        updated_resource = call_action('resource_show', id=resource['id'])

        assert_equals(updated_resource['validation_status'], validation.status)
        assert_equals(
            updated_resource['validation_timestamp'],
            validation.finished.isoformat())

    @mock_uploads
    def test_job_local_paths_are_hidden(self, mock_open):

        invalid_csv = 'id,type\n' + '1,a,\n' * 1010
        invalid_file = StringIO.StringIO()

        invalid_file.write(invalid_csv)

        mock_upload = MockFieldStorage(invalid_file, 'invalid.csv')

        resource = factories.Resource(format='csv', upload=mock_upload)

        invalid_stream = io.BufferedReader(io.BytesIO(invalid_csv))

        with mock.patch('io.open', return_value=invalid_stream):

            run_validation_job(resource)

        validation = Session.query(Validation).filter(
            Validation.resource_id == resource['id']).one()

        source = validation.report['tables'][0]['source']
        assert source.startswith('http')
        assert source.endswith('invalid.csv')

        warning = validation.report['warnings'][0]
        assert_equals(
            warning, 'Table inspection has reached 1000 row(s) limit')

    @mock_uploads
    def test_job_pass_validation_options(self, mock_open):

        invalid_csv = '''

a,b,c
#comment
1,2,3
'''

        validation_options = {
            'headers': 3,
            'skip_rows': ['#']
        }

        invalid_file = StringIO.StringIO()

        invalid_file.write(invalid_csv)

        mock_upload = MockFieldStorage(invalid_file, 'invalid.csv')

        resource = factories.Resource(
            format='csv',
            upload=mock_upload,
            validation_options=validation_options)

        invalid_stream = io.BufferedReader(io.BytesIO(invalid_csv))

        with mock.patch('io.open', return_value=invalid_stream):

            run_validation_job(resource)

        validation = Session.query(Validation).filter(
            Validation.resource_id == resource['id']).one()

        assert_equals(validation.report['valid'], True)

    @mock_uploads
    def test_job_pass_validation_options_string(self, mock_open):

        invalid_csv = '''

a;b;c
#comment
1;2;3
'''

        validation_options = '''{
            "headers": 3,
            "skip_rows": ["#"]
        }'''

        invalid_file = StringIO.StringIO()

        invalid_file.write(invalid_csv)

        mock_upload = MockFieldStorage(invalid_file, 'invalid.csv')

        resource = factories.Resource(
            format='csv',
            upload=mock_upload,
            validation_options=validation_options)

        invalid_stream = io.BufferedReader(io.BytesIO(invalid_csv))

        with mock.patch('io.open', return_value=invalid_stream):

            run_validation_job(resource)

        validation = Session.query(Validation).filter(
            Validation.resource_id == resource['id']).one()

        assert_equals(validation.report['valid'], True)
