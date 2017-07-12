import mock
import json

from ckan.tests.helpers import reset_db
from ckan.tests import factories
from ckan.lib.uploader import ResourceUpload

from ckanext.validation.jobs import run_validation_job, Inspector, uploader


class MockUploader(ResourceUpload):

    def get_path(self, resource_id):
        return '/tmp/example/{}'.format(resource_id)


def mock_get_resource_uploader(data_dict):
    return MockUploader(data_dict)


class TestValidationJob(object):

    def setup(self):
        reset_db()

    @mock.patch.object(Inspector, 'inspect')
    def test_job_run_no_schema(self, mock_inspect):

        resource = factories.Resource(
            url='http://example.com/file.csv', format='csv')

        run_validation_job(resource)

        mock_inspect.assert_called_with(
            'http://example.com/file.csv',
            format='csv',
            schema=None)

    @mock.patch.object(Inspector, 'inspect')
    def test_job_run_schema(self, mock_inspect):

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
    def test_job_run_uploaded_file(self, mock_uploader, mock_inspect):

        resource = factories.Resource(
            url='', url_type='upload', format='csv')

        run_validation_job(resource)

        mock_inspect.assert_called_with(
            '/tmp/example/{}'.format(resource['id']),
            format='csv',
            schema=None)
