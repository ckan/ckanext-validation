import mock
from nose.tools import assert_equals

from ckan.tests.helpers import call_action, reset_db
from ckan.tests import factories
from ckan.tests.helpers import change_config

from ckanext.validation.model import create_tables, tables_exist
from ckanext.validation.jobs import run_validation_job


class TestResourceControllerHooksUpdate(object):

    def setup(self):
        reset_db()
        if not tables_exist():
            create_tables()

    @change_config('ckanext.validation.run_on_create_async', False)
    @mock.patch('ckanext.validation.logic.enqueue_job')
    def test_validation_does_not_run_on_other_fields(self, mock_enqueue):

        resource = {'format': 'CSV'}

        dataset = factories.Dataset(resources=[resource])

        dataset['resources'][0]['description'] = 'Some resource'

        call_action('resource_update', {}, **dataset['resources'][0])

        mock_enqueue.assert_not_called()

    @change_config('ckanext.validation.run_on_create_async', False)
    @mock.patch('ckanext.validation.logic.enqueue_job')
    def test_validation_does_not_run_on_other_formats(self, mock_enqueue):

        resource = {'format': 'PDF'}

        dataset = factories.Dataset(resources=[resource])

        call_action('resource_update', {}, **dataset['resources'][0])

        mock_enqueue.assert_not_called()

    @change_config('ckanext.validation.run_on_create_async', False)
    @mock.patch('ckanext.validation.logic.enqueue_job')
    def test_validation_run_on_upload(self, mock_enqueue):

        resource = {
            'format': 'CSV',
            'upload': 'mock_upload',
            'url_type': 'upload'
        }

        dataset = factories.Dataset(resources=[resource])

        call_action('resource_update', {}, **dataset['resources'][0])

        assert_equals(mock_enqueue.call_count, 1)

        assert_equals(mock_enqueue.call_args[0][0], run_validation_job)
        assert_equals(
            mock_enqueue.call_args[0][1][0]['id'],
            dataset['resources'][0]['id'])

    @change_config('ckanext.validation.run_on_create_async', False)
    @mock.patch('ckanext.validation.logic.enqueue_job')
    def test_validation_run_on_url_change(self, mock_enqueue):

        resource = {'format': 'CSV', 'url': 'https://some.url'}

        dataset = factories.Dataset(resources=[resource])

        dataset['resources'][0]['url'] = 'https://some.new.url'

        call_action('resource_update', {}, **dataset['resources'][0])

        assert_equals(mock_enqueue.call_count, 1)

        assert_equals(mock_enqueue.call_args[0][0], run_validation_job)
        assert_equals(
            mock_enqueue.call_args[0][1][0]['id'],
            dataset['resources'][0]['id'])

    @change_config('ckanext.validation.run_on_create_async', False)
    @mock.patch('ckanext.validation.logic.enqueue_job')
    def test_validation_run_on_schema_change(self, mock_enqueue):

        resource = {
            'url': 'http://some.url',
            'format': 'CSV',
            'schema': {
                'fields': [
                    {'name': 'code'}
                ]
            }
        }

        dataset = factories.Dataset(resources=[resource])

        dataset['resources'][0]['schema'] = {
            'fields': [
                {'name': 'code'},
                {'name': 'date'}
            ]
        }

        call_action('resource_update', {}, **dataset['resources'][0])

        assert_equals(mock_enqueue.call_count, 1)

        assert_equals(mock_enqueue.call_args[0][0], run_validation_job)
        assert_equals(
            mock_enqueue.call_args[0][1][0]['id'],
            dataset['resources'][0]['id'])

    @change_config('ckanext.validation.run_on_create_async', False)
    @mock.patch('ckanext.validation.logic.enqueue_job')
    def test_validation_run_on_format_change(self, mock_enqueue):

        resource = factories.Resource()

        resource['format'] = 'CSV'

        call_action('resource_update', {}, **resource)

        assert_equals(mock_enqueue.call_count, 1)

        assert_equals(mock_enqueue.call_args[0][0], run_validation_job)
        assert_equals(mock_enqueue.call_args[0][1][0]['id'], resource['id'])

    @change_config('ckanext.validation.run_on_create_async', False)
    @change_config('ckanext.validation.run_on_update_async', False)
    @mock.patch('ckanext.validation.logic.enqueue_job')
    def test_validation_does_not_run_when_config_false(self, mock_enqueue):

        resource = factories.Resource(format='CSV')

        resource['url'] = 'http://some.new.url'

        call_action('resource_update', {}, **resource)

        mock_enqueue.assert_not_called()


class TestResourceControllerHooksCreate(object):

    def setup(self):
        reset_db()
        if not tables_exist():
            create_tables()

    @mock.patch('ckanext.validation.logic.enqueue_job')
    def test_validation_does_not_run_on_other_formats(self, mock_enqueue):

        factories.Resource(format='PDF')

        mock_enqueue.assert_not_called()

    @mock.patch('ckanext.validation.logic.enqueue_job')
    @change_config('ckanext.validation.run_on_update_async', False)
    def test_validation_run_with_upload(self, mock_enqueue):

        resource = factories.Resource(format='CSV', url_type='upload')

        assert_equals(mock_enqueue.call_count, 1)

        assert_equals(mock_enqueue.call_args[0][0], run_validation_job)
        assert_equals(mock_enqueue.call_args[0][1][0]['id'], resource['id'])

    @mock.patch('ckanext.validation.logic.enqueue_job')
    @change_config('ckanext.validation.run_on_update_async', False)
    def test_validation_run_with_url(self, mock_enqueue):

        resource = factories.Resource(format='CSV', url='http://some.data')

        assert_equals(mock_enqueue.call_count, 1)

        assert_equals(mock_enqueue.call_args[0][0], run_validation_job)
        assert_equals(mock_enqueue.call_args[0][1][0]['id'], resource['id'])

    @change_config('ckanext.validation.run_on_create_async', False)
    @change_config('ckanext.validation.run_on_update_async', False)
    @mock.patch('ckanext.validation.logic.enqueue_job')
    def test_validation_does_not_run_when_config_false(self, mock_enqueue):

        dataset = factories.Dataset()

        resource = {
            'format': 'CSV',
            'url': 'http://some.data',
            'package_id': dataset['id'],
        }

        call_action('resource_create', {}, **resource)

        mock_enqueue.assert_not_called()


class TestPackageControllerHooksCreate(object):

    def setup(self):
        reset_db()
        if not tables_exist():
            create_tables()

    @mock.patch('ckanext.validation.logic.enqueue_job')
    def test_validation_does_not_run_on_other_formats(self, mock_enqueue):

        factories.Dataset(resources=[{'format': 'PDF'}])

        mock_enqueue.assert_not_called()

    @change_config('ckanext.validation.run_on_create_async', False)
    @mock.patch('ckanext.validation.logic.enqueue_job')
    def test_validation_does_not_run_when_config_false(self, mock_enqueue):

        factories.Dataset(resources=[
            {'format': 'CSV', 'url': 'http://some.data'}])

        mock_enqueue.assert_not_called()

    @mock.patch('ckanext.validation.logic.enqueue_job')
    def test_validation_run_with_upload(self, mock_enqueue):

        resource = {
            'id': 'test-resource-id',
            'format': 'CSV',
            'url_type': 'upload'
        }
        factories.Dataset(resources=[resource])

        assert_equals(mock_enqueue.call_count, 1)

        assert_equals(mock_enqueue.call_args[0][0], run_validation_job)
        assert_equals(mock_enqueue.call_args[0][1][0]['id'], resource['id'])

    @mock.patch('ckanext.validation.logic.enqueue_job')
    def test_validation_run_with_url(self, mock_enqueue):

        resource = {
            'id': 'test-resource-id',
            'format': 'CSV',
            'url': 'http://some.data'
        }
        factories.Dataset(resources=[resource])

        assert_equals(mock_enqueue.call_count, 1)

        assert_equals(mock_enqueue.call_args[0][0], run_validation_job)
        assert_equals(mock_enqueue.call_args[0][1][0]['id'], resource['id'])

    @mock.patch('ckanext.validation.logic.enqueue_job')
    def test_validation_run_only_supported_formats(self, mock_enqueue):

        resource1 = {
            'id': 'test-resource-id-1',
            'format': 'CSV',
            'url': 'http://some.data'
        }
        resource2 = {
            'id': 'test-resource-id-2',
            'format': 'PDF',
            'url': 'http://some.doc'
        }

        factories.Dataset(resources=[resource1, resource2])

        assert_equals(mock_enqueue.call_count, 1)

        assert_equals(mock_enqueue.call_args[0][0], run_validation_job)
        assert_equals(mock_enqueue.call_args[0][1][0]['id'], resource1['id'])


class TestPackageControllerHooksUpdate(object):

    def setup(self):
        reset_db()
        if not tables_exist():
            create_tables()

    @change_config('ckanext.validation.run_on_create_async', False)
    @mock.patch('ckanext.validation.logic.enqueue_job')
    def test_validation_runs_with_url(self, mock_enqueue):

        resource = {
            'id': 'test-resource-id',
            'format': 'CSV',
            'url': 'http://some.data'
        }
        dataset = factories.Dataset(resources=[resource], id='myid')

        mock_enqueue.assert_not_called()

        dataset['resources'][0]['url'] = 'http://some.other.data'

        call_action('package_update', {}, **dataset)

        assert_equals(mock_enqueue.call_count, 1)

        assert_equals(mock_enqueue.call_args[0][0], run_validation_job)
        assert_equals(mock_enqueue.call_args[0][1][0]['id'], resource['id'])

    @change_config('ckanext.validation.run_on_create_async', False)
    @mock.patch('ckanext.validation.logic.enqueue_job')
    def test_validation_runs_with_upload(self, mock_enqueue):

        resource = {
            'id': 'test-resource-id',
            'format': 'CSV',
            'url_type': 'upload'
        }
        dataset = factories.Dataset(resources=[resource])

        mock_enqueue.assert_not_called()

        dataset['resources'][0]['url'] = 'http://some.other.data'

        call_action('package_update', {}, **dataset)

        assert_equals(mock_enqueue.call_count, 1)

        assert_equals(mock_enqueue.call_args[0][0], run_validation_job)
        assert_equals(mock_enqueue.call_args[0][1][0]['id'], resource['id'])

    @change_config('ckanext.validation.run_on_create_async', False)
    @mock.patch('ckanext.validation.logic.enqueue_job')
    def test_validation_does_not_run_on_other_formats(self, mock_enqueue):

        resource = {
            'id': 'test-resource-id',
            'format': 'PDF',
            'url': 'http://some.doc'
        }
        dataset = factories.Dataset(resources=[resource])

        mock_enqueue.assert_not_called()

        dataset['resources'][0]['url'] = 'http://some.other.doc'

        call_action('package_update', {}, **dataset)

        mock_enqueue.assert_not_called()

    @change_config('ckanext.validation.run_on_create_async', False)
    @mock.patch('ckanext.validation.logic.enqueue_job')
    def test_validation_run_only_supported_formats(self, mock_enqueue):

        resource1 = {
            'id': 'test-resource-id-1',
            'format': 'CSV',
            'url': 'http://some.data'
        }
        resource2 = {
            'id': 'test-resource-id-2',
            'format': 'PDF',
            'url': 'http://some.doc'
        }

        dataset = factories.Dataset(resources=[resource1, resource2])

        mock_enqueue.assert_not_called()

        dataset['resources'][0]['url'] = 'http://some.other.data'

        call_action('package_update', {}, **dataset)

        assert_equals(mock_enqueue.call_count, 1)

        assert_equals(mock_enqueue.call_args[0][0], run_validation_job)
        assert_equals(mock_enqueue.call_args[0][1][0]['id'], resource1['id'])

    @change_config('ckanext.validation.run_on_create_async', False)
    @change_config('ckanext.validation.run_on_update_async', False)
    @mock.patch('ckanext.validation.logic.enqueue_job')
    def test_validation_does_not_run_when_config_false(self, mock_enqueue):

        resource = {
            'id': 'test-resource-id',
            'format': 'CSV',
            'url': 'http://some.data'
        }
        dataset = factories.Dataset(resources=[resource])

        call_action('package_update', {}, **dataset)

        mock_enqueue.assert_not_called()
