import mock
import json

from nose.tools import assert_equals

from ckan.model import Session
from ckan.lib.uploader import ResourceUpload
from ckan.tests.helpers import reset_db
from ckan.tests import factories

from ckanext.validation.model import create_tables, tables_exist, Validation
from ckanext.validation.jobs import run_validation_job, Inspector, uploader


class MockUploader(ResourceUpload):

    def get_path(self, resource_id):
        return '/tmp/example/{}'.format(resource_id)


def mock_get_resource_uploader(data_dict):
    return MockUploader(data_dict)


mock_report_valid = {
    'error-count': 0,
    'table-count': 1,
    'tables': [
        {
            'error-count': 0,
            'errors': [],
            'headers': [
                'name',
                'ward',
                'party',
                'other'
            ],
            'row-count': 79,
            'source': 'http://example.com/valid.csv',
            'time': 0.007,
            'valid': True
        }
    ],
    'time': 0.009,
    'valid': True,
    'warnings': []
}


mock_report_invalid = {
    'error-count': 2,
    'table-count': 1,
    'tables': [
        {
            'error-count': 2,
            'errors': [
                {
                    'code': 'blank-header',
                    'column-number': 3,
                    'message': 'Header in column 3 is blank',
                    'row': None,
                    'row-number': None
                },
                {
                    'code': 'duplicate-header',
                    'column-number': 4,
                    'message': 'Header in column 4 is duplicated to ...',
                    'row': None,
                    'row-number': None
                },
            ],
            'headers': [
                'name',
                'ward',
                'party',
                'other'
            ],
            'row-count': 79,
            'source': 'http://example.com/valid.csv',
            'time': 0.007,
            'valid': False
        }
    ],
    'time': 0.009,
    'valid': False,
    'warnings': []
}


mock_report_error = {
    'error-count': 0,
    'table-count': 0,
    'warnings': ['Some warning'],
}


class TestValidationJob(object):

    def setup(self):
        reset_db()
        if not tables_exist():
            create_tables()

    @mock.patch.object(Inspector, 'inspect')
    @mock.patch.object(Session, 'commit')
    def test_job_run_no_schema(self, mock_commit, mock_inspect):

        resource = factories.Resource(
            url='http://example.com/file.csv', format='csv')

        run_validation_job(resource)

        mock_inspect.assert_called_with(
            'http://example.com/file.csv',
            format='csv',
            schema=None)

    @mock.patch.object(Inspector, 'inspect')
    @mock.patch.object(Session, 'commit')
    def test_job_run_schema(self, mock_commit, mock_inspect):

        schema = {
            'fields': [
                {'name': 'id', 'type': 'integer'},
                {'name': 'description', 'type': 'string'}
            ]
        }

        resource = factories.Resource(
            url='http://example.com/file.csv', format='csv',
            schema=json.dumps(schema))

        run_validation_job(resource)

        mock_inspect.assert_called_with(
            'http://example.com/file.csv',
            format='csv',
            schema=schema)

    @mock.patch.object(Inspector, 'inspect')
    @mock.patch.object(uploader, 'get_resource_uploader',
                       return_value=mock_get_resource_uploader({}))
    @mock.patch.object(Session, 'commit')
    def test_job_run_uploaded_file(
            self, mock_commit, mock_uploader, mock_inspect):

        resource = factories.Resource(
            url='', url_type='upload', format='csv')

        run_validation_job(resource)

        mock_inspect.assert_called_with(
            '/tmp/example/{}'.format(resource['id']),
            format='csv',
            schema=None)

    @mock.patch.object(Inspector, 'inspect', return_value=mock_report_valid)
    def test_job_run_valid_stores_validation_object(self, mock_inspect):

        resource = factories.Resource(
            url='http://example.com/file.csv', format='csv')

        run_validation_job(resource)

        validation = Session.query(Validation).filter(
            Validation.resource_id == resource['id']).one()

        assert_equals(validation.status, 'success')
        assert_equals(validation.report, mock_report_valid)
        assert validation.finished

    @mock.patch.object(Inspector, 'inspect', return_value=mock_report_invalid)
    def test_job_run_invalid_stores_validation_object(self, mock_inspect):

        resource = factories.Resource(
            url='http://example.com/file.csv', format='csv')

        run_validation_job(resource)

        validation = Session.query(Validation).filter(
            Validation.resource_id == resource['id']).one()

        assert_equals(validation.status, 'failure')
        assert_equals(validation.report, mock_report_invalid)
        assert validation.finished

    @mock.patch.object(Inspector, 'inspect', return_value=mock_report_error)
    def test_job_run_error_stores_validation_object(self, mock_inspect):

        resource = factories.Resource(
            url='http://example.com/file.csv', format='csv')

        run_validation_job(resource)

        validation = Session.query(Validation).filter(
            Validation.resource_id == resource['id']).one()

        assert_equals(validation.status, 'error')
        assert_equals(validation.report, None)
        assert_equals(validation.error, {'message': 'Some warning'})
        assert validation.finished
