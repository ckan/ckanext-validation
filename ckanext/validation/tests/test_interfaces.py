import mock
import pytest

from ckan import plugins as p
from ckan.tests import helpers, factories

import ckantoolkit as t

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


@pytest.mark.usefixtures("clean_db", "validation_setup", "with_plugins")
@pytest.mark.ckan_config("ckan.plugins", "validation test_validation_plugin scheming_datasets")
class TestInterfaceSync(BaseTestInterfaces):
    @classmethod
    def setup_class(cls):
        # Needed to apply the config changes at the right time so they can be picked up
        # during startup
        cls._original_config = dict(t.config)
        t.config["ckanext.validation.run_on_create_sync"] = True
        t.config["ckanext.validation.run_on_update_sync"] = True

    @classmethod
    def teardown_class(cls):

        t.config.clear()
        t.config.update(cls._original_config)

    @pytest.mark.ckan_config('ckanext.validation.run_on_create_async', False)
    @pytest.mark.ckan_config('ckanext.validation.run_on_update_async', False)
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
        assert _get_plugin_calls() == 2  # One for create and one for update

        assert mock_validation.called

    @pytest.mark.ckan_config('ckanext.validation.run_on_create_async', False)
    @pytest.mark.ckan_config('ckanext.validation.run_on_update_async', False)
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
        assert _get_plugin_calls() == 2  # One for create and one for update

        assert not mock_validation.called

@pytest.mark.usefixtures("clean_db", "validation_setup", "with_plugins")
@pytest.mark.ckan_config("ckan.plugins", "validation test_validation_plugin scheming_datasets")
class TestInterfaceAsync(BaseTestInterfaces):

    @classmethod
    def _apply_config_changes(cls, cfg):
        cfg['ckanext.validation.run_on_create_sync'] = False
        cfg['ckanext.validation.run_on_update_sync'] = False

    @pytest.mark.ckan_config('ckanext.validation.run_on_create_async', True)
    @mock.patch('ckanext.validation.logic.enqueue_job')
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
    @mock.patch('ckanext.validation.logic.enqueue_job')
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
    @mock.patch('ckanext.validation.logic.enqueue_job')
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
    @mock.patch('ckanext.validation.logic.enqueue_job')
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
