from unittest import mock
import pytest

from ckan import plugins as p
from ckan.tests import helpers, factories

from ckanext.validation.interfaces import IDataValidation
from ckanext.validation.tests.helpers import VALID_REPORT


class TestPlugin(p.SingletonPlugin):

    p.implements(IDataValidation, inherit=True)

    calls = 0

    def reset_counter(self):
        self.calls = 0

    def can_validate(self, context, data_dict):
        self.calls += 1

        if data_dict.get('my_custom_field') == 'xx':
            return False

        return True


def _get_plugin_calls():
    for plugin in p.PluginImplementations(IDataValidation):
        return plugin.calls


class BaseTestInterfaces(object):

    def setup(self):

        for plugin in p.PluginImplementations(IDataValidation):
            return plugin.reset_counter()


@pytest.fixture
def reset_counter():
    for plugin in p.PluginImplementations(IDataValidation):
        return plugin.reset_counter()


@pytest.mark.usefixtures("clean_db", "validation_setup", "with_plugins", "reset_counter")
@pytest.mark.ckan_config("ckan.plugins", "validation test_validation_plugin scheming_datasets")
class TestInterfaceSync():

    @pytest.mark.ckan_config('ckanext.validation.run_on_create_async', False)
    @pytest.mark.ckan_config('ckanext.validation.run_on_update_async', False)
    @pytest.mark.ckan_config('ckanext.validation.run_on_create_sync', True)
    @mock.patch('ckanext.validation.jobs.validate',
                return_value=VALID_REPORT)
    def test_can_validate_called_on_create_sync(self, mock_validation):

        dataset = factories.Dataset()
        helpers.call_action(
            'resource_create',
            url='https://example.com/data.csv',
            format='CSV',
            package_id=dataset['id']
        )
        assert _get_plugin_calls() == 1

        assert mock_validation.called

    @pytest.mark.ckan_config('ckanext.validation.run_on_create_async', False)
    @pytest.mark.ckan_config('ckanext.validation.run_on_update_async', False)
    @pytest.mark.ckan_config('ckanext.validation.run_on_create_sync', True)
    @mock.patch('ckanext.validation.jobs.validate')
    def test_can_validate_called_on_create_sync_no_validation(self, mock_validation):

        dataset = factories.Dataset()
        helpers.call_action(
            'resource_create',
            url='https://example.com/data.csv',
            format='CSV',
            package_id=dataset['id'],
            my_custom_field='xx',
        )
        assert _get_plugin_calls() == 1

        assert not mock_validation.called

    @pytest.mark.ckan_config('ckanext.validation.run_on_create_async', False)
    @pytest.mark.ckan_config('ckanext.validation.run_on_update_async', False)
    @pytest.mark.ckan_config('ckanext.validation.run_on_update_sync', True)
    @mock.patch('ckanext.validation.jobs.validate',
                return_value=VALID_REPORT)
    def test_can_validate_called_on_update_sync(self, mock_validation):

        dataset = factories.Dataset()
        resource = factories.Resource(package_id=dataset['id'])
        helpers.call_action(
            'resource_update',
            id=resource['id'],
            url='https://example.com/data.csv',
            format='CSV',
            package_id=dataset['id']
        )
        # One for the resource_update, one for the resource_patch one
        # to store the result, which does not trigger another job
        assert _get_plugin_calls() == 2

        assert mock_validation.called

    @pytest.mark.ckan_config('ckanext.validation.run_on_create_async', False)
    @pytest.mark.ckan_config('ckanext.validation.run_on_update_async', False)
    @pytest.mark.ckan_config('ckanext.validation.run_on_update_sync', True)
    @mock.patch('ckanext.validation.jobs.validate')
    def test_can_validate_called_on_update_sync_no_validation(self, mock_validation):

        dataset = factories.Dataset()
        resource = factories.Resource(package_id=dataset['id'])
        helpers.call_action(
            'resource_update',
            id=resource['id'],
            url='https://example.com/data.csv',
            format='CSV',
            package_id=dataset['id'],
            my_custom_field='xx',
        )
        assert _get_plugin_calls() == 1

        assert not mock_validation.called


@pytest.mark.usefixtures("clean_db", "validation_setup", "with_plugins", "reset_counter")
@pytest.mark.ckan_config("ckan.plugins", "validation test_validation_plugin scheming_datasets")
@pytest.mark.ckan_config('ckanext.validation.run_on_create_sync', False)
@pytest.mark.ckan_config('ckanext.validation.run_on_update_sync', False)
class TestInterfaceAsync():

    @pytest.mark.ckan_config('ckanext.validation.run_on_create_async', True)
    @mock.patch('ckanext.validation.logic.action.enqueue_job')
    def test_can_validate_called_on_create_async(self, mock_validation):

        dataset = factories.Dataset()
        helpers.call_action(
            'resource_create',
            url='https://example.com/data.csv',
            format='CSV',
            package_id=dataset['id']
        )
        assert _get_plugin_calls() == 1

        assert mock_validation.called

    @pytest.mark.ckan_config('ckanext.validation.run_on_create_async', True)
    @mock.patch('ckanext.validation.logic.action.enqueue_job')
    def test_can_validate_called_on_create_async_no_validation(self, mock_validation):

        dataset = factories.Dataset()
        helpers.call_action(
            'resource_create',
            url='https://example.com/data.csv',
            format='CSV',
            package_id=dataset['id'],
            my_custom_field='xx',
        )
        assert _get_plugin_calls() == 1

        assert not mock_validation.called

    @pytest.mark.ckan_config('ckanext.validation.run_on_create_async', False)
    @pytest.mark.ckan_config('ckanext.validation.run_on_update_async', True)
    @mock.patch('ckanext.validation.logic.action.enqueue_job')
    def test_can_validate_called_on_update_async(self, mock_validation):

        dataset = factories.Dataset()
        resource = factories.Resource(package_id=dataset['id'])
        helpers.call_action(
            'resource_update',
            id=resource['id'],
            url='https://example.com/data.csv',
            format='CSV',
            package_id=dataset['id']
        )
        assert _get_plugin_calls() == 1

        assert mock_validation.called

    @pytest.mark.ckan_config('ckanext.validation.run_on_create_async', False)
    @pytest.mark.ckan_config('ckanext.validation.run_on_update_async', True)
    @mock.patch('ckanext.validation.logic.action.enqueue_job')
    def test_can_validate_called_on_update_async_no_validation(self, mock_validation):

        dataset = factories.Dataset()
        resource = factories.Resource(package_id=dataset['id'])
        helpers.call_action(
            'resource_update',
            id=resource['id'],
            url='https://example.com/data.csv',
            format='CSV',
            package_id=dataset['id'],
            my_custom_field='xx',

        )
        assert _get_plugin_calls() == 1

        assert not mock_validation.called
