# encoding: utf-8

import io
import json
from faker import Faker

import responses
import pytest
from unittest.mock import patch

from ckan.plugins import toolkit
from ckan.lib.uploader import ResourceUpload
from ckan.tests.helpers import call_action
from ckan.tests import factories

from ckanext.validation import settings as s
from ckanext.validation.model import Validation
from ckanext.validation.jobs import (
    run_validation_job,
    uploader,
    Session,
    requests,
)
from .helpers import (
    INVALID_REPORT,
    VALID_REPORT,
    ERROR_REPORT,
    VALID_CSV,
    INVALID_CSV,
    SCHEMA,
    MockFileStorage,
    MOCK_ASYNC_VALIDATE,
)


class MockUploader(ResourceUpload):

    def get_path(self, resource_id):
        return '/tmp/example/{}'.format(resource_id)


def mock_get_resource_uploader(data_dict):
    return MockUploader(data_dict)


@pytest.mark.usefixtures("clean_db", "validation_setup")
@pytest.mark.ckan_config(s.ASYNC_UPDATE_KEY, True)
@pytest.mark.ckan_config(s.ASYNC_CREATE_KEY, True)
class TestValidationJob(object):

    @patch(MOCK_ASYNC_VALIDATE, return_value=VALID_REPORT)
    @patch.object(Session, 'commit')
    @patch.object(toolkit, 'get_action')
    @patch.object(requests, 'Session', return_value='Some_Session')
    def test_job_run_no_schema(self, mock_requests, mock_get_action,
                               mock_commit, mock_validate, dataset):
        resource = {
            'id': 'test',
            'url': 'http://example.com/file.csv',
            'format': 'csv',
            'package_id': dataset['id'],
        }

        run_validation_job(resource)

        mock_validate.assert_called_with('http://example.com/file.csv',
                                         format='csv',
                                         schema=None)

    @patch(MOCK_ASYNC_VALIDATE, return_value=VALID_REPORT)
    @patch.object(Session, 'commit')
    @patch.object(toolkit, 'get_action')
    @patch.object(requests, 'Session', return_value='Some_Session')
    def test_job_run_schema(self, mock_requests, mock_get_action, mock_commit,
                            mock_validate, dataset):
        json_schema = json.dumps(SCHEMA)
        resource = {
            'id': Faker().uuid4(),
            'url': 'http://example.com/file.csv',
            'format': 'csv',
            'schema': json_schema,
            'package_id': dataset['id'],
        }

        run_validation_job(resource)

        assert mock_validate.call_args[0][0] == "http://example.com/file.csv"
        assert mock_validate.call_args[1]["format"] == "csv"
        assert mock_validate.call_args[1]["schema"].to_dict() == SCHEMA
        # mock_validate.assert_called_with('http://example.com/file.csv',
        #                                  format='csv',
        #                                  schema=json_schema)

    @patch(MOCK_ASYNC_VALIDATE, return_value=VALID_REPORT)
    @patch.object(uploader, 'get_resource_uploader',
                  return_value=mock_get_resource_uploader({}))
    @patch.object(Session, 'commit')
    @patch.object(toolkit, 'get_action')
    @patch.object(requests, 'Session', return_value='Some_Session')
    def test_job_run_uploaded_file(self, mock_requests, mock_get_action,
                                   mock_commit, mock_uploader, mock_validate,
                                   dataset):
        resource = {
            'id': Faker().uuid4(),
            'url': '__upload',
            'url_type': 'upload',
            'format': 'csv',
            'package_id': dataset['id'],
        }

        run_validation_job(resource)

        mock_validate.assert_called_with('/tmp/example/{}'.format(
            resource['id']),
            format='csv',
            schema=None)

    @patch("ckanext.validation.jobs.validate", return_value=VALID_REPORT)
    def test_job_run_valid_stores_validation_object(self, mocked_responses):
        url = 'http://example.com/file.csv'

        mocked_responses.add(responses.GET, url, body=VALID_CSV)
        resource = factories.Resource(url=url, format='csv')

        run_validation_job(resource)

        validation = Session.query(Validation).filter(
            Validation.resource_id == resource['id']).one()

        report = json.loads(validation.report)
        assert validation.status == 'success'
        assert report == VALID_REPORT
        assert report['valid'] is True
        assert report['tasks'][0]['place'] == url
        assert validation.finished

    @patch(MOCK_ASYNC_VALIDATE, return_value=INVALID_REPORT)
    def test_job_run_invalid_stores_validation_object(self, mock_report,
                                                      resource_factory):
        url = "http://example.com/invalid.csv"
        resource = resource_factory(do_not_validate=True, url=url)

        run_validation_job(resource)

        validation = Session.query(Validation).filter(
            Validation.resource_id == resource['id']).one()

        assert validation.status == 'failure'
        report = json.loads(validation.report)
        assert report == INVALID_REPORT
        assert validation.finished

    @patch(MOCK_ASYNC_VALIDATE, return_value=ERROR_REPORT)
    def test_job_run_error_stores_validation_object(self, mock_validate, resource_factory):
        resource = resource_factory()

        run_validation_job(resource)

        validation = Session.query(Validation).filter(
            Validation.resource_id == resource['id']).one()

        assert validation.status == 'error'
        assert json.loads(validation.report) == ERROR_REPORT
        assert validation.error == {'message': ["{'type': 'source-error', 'title': 'Source Error', 'description': 'Data reading error because of not supported or inconsistent contents.', 'message': 'The data source has not supported or has inconsistent contents: the source is empty', 'tags': [], 'note': 'the source is empty'}"]}
        assert validation.finished

    def test_job_run_uploaded_file_replaces_paths(self, resource_factory):

        resource = resource_factory()

        run_validation_job(resource)

        validation = Session.query(Validation).filter(
            Validation.resource_id == resource['id']).one()

        assert json.loads(validation.report)['tasks'][0]['place'].startswith('http')

    def test_job_run_valid_stores_status_in_resource(self, resource_factory):
        resource = resource_factory(do_not_validate=True)
        run_validation_job(resource)

        validation = Session.query(Validation).filter(
            Validation.resource_id == resource['id']).one()

        res = call_action('resource_show', id=resource['id'])

        assert res['validation_status'] == validation.status
        assert res['validation_timestamp'] == validation.finished.isoformat()

    def test_job_local_paths_are_hidden(self, resource_factory):
        """Local path for a resource file must be hidden inside report"""
        upload = MockFileStorage(io.BytesIO(INVALID_CSV), 'invalid.csv')
        resource = resource_factory(upload=upload, do_not_validate=True)

        run_validation_job(resource)

        validation = Session.query(Validation).filter(
            Validation.resource_id == resource['id']).one()

        source = json.loads(validation.report)['tasks'][0]['place']
        assert source.startswith('http')
        assert source.endswith('invalid.csv')

    def test_job_pass_validation_options(self, resource_factory):
        valid_csv = b'''a,b,c,d
#comment
1,2,3,4'''

        upload = MockFileStorage(io.BytesIO(valid_csv), 'valid.csv')

        validation_options = {
            "dialect": {
                "header": True,
                "headerRows": [1],
                "commentChar": "#",
                "csv": {
                    "delimiter": ","
                }
            }
        }

        resource = resource_factory(upload=upload,
                                    validation_options=validation_options,
                                    do_not_validate=True)

        run_validation_job(resource)

        validation = Session.query(Validation).filter(
            Validation.resource_id == resource['id']).one()

        assert '"valid": true' in str(validation.report)

    def test_job_pass_validation_options_string_goodtables_options(self, resource_factory):
        invalid_csv = b'''a;b;c;d
#comment
1;2;3;4
'''

        validation_options = '''{
    "headers": 1,
    "skip_rows": ["#"],
    "delimiter": ";"
}'''

        mock_upload = MockFileStorage(io.BytesIO(invalid_csv), 'invalid.csv')

        resource = resource_factory(upload=mock_upload,
                                    validation_options=validation_options,
                                    do_not_validate=True)

        def invalid_stream(*args, **kwargs):
            return io.BufferedReader(io.BytesIO(invalid_csv))

        with patch("io.open", side_effect=invalid_stream):
            run_validation_job(resource)

        validation = Session.query(Validation).filter(
            Validation.resource_id == resource['id']).one()

        assert '"valid": true' in str(validation.report)
        report = json.loads(validation.report)
        assert report["valid"] is True
