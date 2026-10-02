# encoding: utf-8
import io

from faker import Faker
import pytest
from unittest.mock import patch

from ckan.tests.helpers import call_action
from ckan.tests import factories

import ckanext.validation.settings as s
from . import helpers
from ckanext.validation.jobs import run_validation_job


def _assert_validation_enqueued(mock_enqueue, resource_id):
    assert mock_enqueue.call_count == 1

    assert mock_enqueue.call_args[1]['fn'] == run_validation_job
    assert mock_enqueue.call_args[1]['kwargs']['resource'] == resource_id


@pytest.mark.usefixtures("with_plugins", "validation_setup")
@pytest.mark.ckan_config(s.ASYNC_UPDATE_KEY, True)
# We want to test when updates enqueue a job,
# therefore creates should not enqueue anything (would confuse the test).
@pytest.mark.ckan_config(s.ASYNC_CREATE_KEY, False)
@patch(helpers.MOCK_SYNC_VALIDATE, return_value=helpers.VALID_REPORT)
@patch(helpers.MOCK_ENQUEUE_JOB, return_value=True)
class TestResourceControllerHooksUpdate(object):

    def test_validation_does_not_run_on_other_fields(self, mock_enqueue, mock_sync):
        """Validation should not be triggered during an update, as a description
        change is not a sufficient change to revalidate the resource"""
        resource = factories.Resource(format="CSV",
                                      schema=helpers.SCHEMA,
                                      url="https://some.url")

        mock_enqueue.assert_not_called()

        resource['description'] = 'Some resource'

        call_action('resource_update', **resource)

        mock_enqueue.assert_not_called()

    def test_validation_does_not_run_on_other_formats(self, mock_enqueue, mock_sync):
        """PDF and TTF formats are not supported"""
        resource = factories.Resource(format="PDF", schema=helpers.SCHEMA)

        mock_enqueue.assert_not_called()

        resource["format"] = "TTF"

        call_action('resource_update', **resource)

        mock_enqueue.assert_not_called()

    def test_validation_run_on_upload(self, mock_enqueue, mock_sync):
        """Validation must be triggered during update on upload new file"""
        mock_upload = helpers.MockFileStorage(io.BytesIO(helpers.VALID_CSV),
                                              'valid.csv')

        resource = factories.Resource(format="csv", schema=helpers.SCHEMA)
        mock_enqueue.assert_not_called()

        resource['upload'] = mock_upload

        call_action('resource_update', **resource)

        _assert_validation_enqueued(mock_enqueue, resource['id'])

    def test_validation_run_on_url_change(self, mock_enqueue, mock_sync):
        """Validation must be triggered during update on changing URL"""
        resource = factories.Resource(format="CSV", schema=helpers.SCHEMA)
        mock_enqueue.assert_not_called()

        resource['url'] = "https://some.new.url"

        call_action('resource_update', **resource)

        _assert_validation_enqueued(mock_enqueue, resource['id'])

    def test_validation_run_on_schema_change(self, mock_enqueue, mock_sync):
        """Validation must be triggered during update on changing URL"""
        resource = factories.Resource(format="CSV")
        mock_enqueue.assert_not_called()

        resource['schema'] = helpers.NEW_SCHEMA

        call_action('resource_update', **resource)

        _assert_validation_enqueued(mock_enqueue, resource['id'])

    def test_validation_run_on_format_change(self, mock_enqueue, mock_sync):
        """Validation must be triggered during update on changing format"""
        resource = factories.Resource(format="PDF", schema=helpers.SCHEMA)

        mock_enqueue.assert_not_called()

        resource['format'] = 'CSV'

        call_action('resource_update', {'defer_commit': True}, **resource)

        _assert_validation_enqueued(mock_enqueue, resource['id'])

    def test_validation_run_on_validation_options_change(
            self, mock_enqueue, mock_sync):
        """Validation must be triggered during update on changing
        validation_options"""
        resource = factories.Resource(format="CSV", schema=helpers.SCHEMA)
        mock_enqueue.assert_not_called()

        mock_enqueue.assert_not_called()

        resource['validation_options'] = {'headers': 1, 'skip_rows': ['#']}

        call_action('resource_update', **resource)

        _assert_validation_enqueued(mock_enqueue, resource['id'])


@pytest.mark.usefixtures("with_plugins", "validation_setup")
@pytest.mark.ckan_config(s.ASYNC_UPDATE_KEY, True)
@pytest.mark.ckan_config(s.ASYNC_CREATE_KEY, True)
@patch(helpers.MOCK_ENQUEUE_JOB)
class TestResourceControllerHooksCreate(object):

    def test_validation_does_not_run_on_other_formats(self, mock_enqueue):
        factories.Resource(format='PDF', schema=helpers.SCHEMA)

        mock_enqueue.assert_not_called()

    def test_validation_runs_with_upload(self, mock_enqueue):
        factories.Resource(format="CSV", schema=helpers.SCHEMA)

        mock_enqueue.assert_called()

    def test_validation_run_with_url(self, mock_enqueue):
        resource = factories.Resource(url='http://some.data', format="CSV", schema=helpers.SCHEMA)

        _assert_validation_enqueued(mock_enqueue, resource['id'])


@pytest.mark.usefixtures("with_plugins", "validation_setup")
@pytest.mark.ckan_config(s.ASYNC_UPDATE_KEY, True)
@pytest.mark.ckan_config(s.ASYNC_CREATE_KEY, True)
@patch(helpers.MOCK_ENQUEUE_JOB)
class TestPackageControllerHooksCreate(object):

    def test_validation_does_not_run_on_other_formats(self, mock_enqueue):
        factories.Dataset(resources=[{'format': 'PDF'}])

        mock_enqueue.assert_not_called()

    def test_validation_run_with_upload(self, mock_enqueue):
        resource = {
            'id': Faker().uuid4(),
            'format': 'CSV',
            'url_type': 'upload',
            'schema': helpers.SCHEMA
        }
        factories.Dataset(resources=[resource])

        _assert_validation_enqueued(mock_enqueue, resource['id'])

    def test_validation_run_with_url(self, mock_enqueue):
        resource = {
            'id': Faker().uuid4(),
            'format': 'CSV',
            'url': 'http://some.data',
            'schema': helpers.SCHEMA
        }

        factories.Dataset(resources=[resource])

        _assert_validation_enqueued(mock_enqueue, resource['id'])

    def test_validation_run_only_supported_formats(self, mock_enqueue):

        resource1 = {
            'id': Faker().uuid4(),
            'format': 'CSV',
            'url': 'http://some.data',
            'schema': helpers.SCHEMA
        }
        resource2 = {
            'id': Faker().uuid4(),
            'format': 'PDF',
            'url': 'http://some.doc',
            'schema': helpers.SCHEMA
        }

        factories.Dataset(resources=[resource1, resource2])

        _assert_validation_enqueued(mock_enqueue, resource1['id'])


@pytest.mark.usefixtures("with_plugins", "validation_setup")
@pytest.mark.ckan_config(s.ASYNC_UPDATE_KEY, True)
@pytest.mark.ckan_config(s.ASYNC_CREATE_KEY, False)
@patch(helpers.MOCK_SYNC_VALIDATE, return_value=helpers.VALID_REPORT)
@patch(helpers.MOCK_ENQUEUE_JOB, return_value=True)
class TestPackageControllerHooksUpdate(object):

    def test_validation_runs_with_url(self, mock_enqueue, mock_sync):
        package = factories.Dataset(resources=[{
            "format": "CSV",
            "schema": helpers.SCHEMA,
            "url": "http://some.data"
        }])

        assert mock_enqueue.call_count == 0

        package['resources'][0]['url'] = 'http://some.other.data'

        call_action('package_update', **package)

        assert mock_enqueue.call_count == 1

    def test_validation_does_not_run_on_other_formats(self, mock_enqueue, mock_sync):

        resource = {
            'id': Faker().uuid4(),
            'format': 'PDF',
            'url': 'http://some.doc'
        }
        dataset = factories.Dataset(resources=[resource])

        mock_enqueue.assert_not_called()

        dataset['resources'][0]['url'] = 'http://some.other.doc'

        call_action('package_update', **dataset)

        mock_enqueue.assert_not_called()

    def test_validation_run_only_supported_formats(self, mock_enqueue, mock_sync):

        resource1 = {
            'id': Faker().uuid4(),
            'format': 'CSV',
            'url': 'http://some.data',
            'schema': helpers.SCHEMA
        }
        resource2 = {
            'id': Faker().uuid4(),
            'format': 'PDF',
            'url': 'http://some.doc',
            'schema': helpers.SCHEMA
        }

        dataset = factories.Dataset(resources=[resource1, resource2])

        mock_enqueue.assert_not_called()

        dataset['resources'][0]['url'] = 'http://some.other.data'

        call_action('package_update', **dataset)
        # one resource must be validated during update
        mock_enqueue.assert_called()

        _assert_validation_enqueued(mock_enqueue, resource1['id'])
