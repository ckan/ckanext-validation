# encoding: utf-8

import sys
import traceback

import pytest
from unittest.mock import patch

from ckan import plugins as p
from ckan.tests.helpers import call_action

import ckanext.validation.tests.helpers as helpers
from ckanext.validation import settings
from ckanext.validation.interfaces import IDataValidation, IPipeValidation


class TestPlugin(p.SingletonPlugin):

    p.implements(IDataValidation, inherit=True)
    p.implements(IPipeValidation, inherit=True)

    calls = 0

    def reset_counter(self):
        self.calls = 0

    # IDataValidation

    def can_validate(self, context, data_dict):
        self.calls += 1
        print("Logging call %s to can_validate" % self.calls, file=sys.stderr)
        traceback.print_stack(file=sys.stderr)

        if data_dict.get('do_not_validate'):
            return False

        return True

    def set_create_mode(self, context, data_dict, current_mode):
        is_async = data_dict.get('async')
        return settings.ASYNC_MODE if is_async else current_mode

    def set_update_mode(self, context, data_dict, current_mode):
        is_async = data_dict.get('async')
        return settings.ASYNC_MODE if is_async else current_mode

    # IPipeValidation

    def receive_validation_report(self, validation_report):
        self.calls += 1
        print("Logging call %s to receive_validation_report" % self.calls, file=sys.stderr)
        traceback.print_stack(file=sys.stderr)


def _reset_plugin_counter():
    for plugin in p.PluginImplementations(IDataValidation):
        plugin.reset_counter()


def _get_data_plugin_calls():
    for plugin in p.PluginImplementations(IDataValidation):
        return plugin.calls


def _get_pipe_plugin_calls():
    for plugin in p.PluginImplementations(IPipeValidation):
        return plugin.calls


class BaseTestInterfaces(object):

    def setup(self):
        for plugin in p.PluginImplementations(IDataValidation):
            return plugin.reset_counter()

        for plugin in p.PluginImplementations(IPipeValidation):
            return plugin.reset_counter()


@pytest.mark.usefixtures("clean_db", "validation_setup")
@patch(helpers.MOCK_SYNC_VALIDATE, return_value=helpers.VALID_REPORT)
class TestInterfaceSync(BaseTestInterfaces):

    def test_can_validate_called_on_create_sync(self, mock_validation,
                                                resource_factory):
        _reset_plugin_counter()
        """Plugin must be called once for SYNC mode on create
        1. resource before_create
        """
        resource_factory()

        assert _get_data_plugin_calls() == 1
        assert _get_pipe_plugin_calls() == 1
        assert mock_validation.called

    def test_can_validate_called_on_create_sync_no_validation(
            self, mock_validation, resource_factory):
        _reset_plugin_counter()
        """Plugin must be called once for SYNC mode on create
        1. resource before_create
        """
        resource_factory(do_not_validate=True)

        assert _get_data_plugin_calls() == 1
        assert _get_pipe_plugin_calls() == 1
        assert not mock_validation.called

    def test_can_validate_called_on_update_sync(self, mock_validation,
                                                resource_factory):
        _reset_plugin_counter()
        """Plugin must be called 2 times for SYNC mode.
        1. resource before_create on resource create
        2. resource before_update on resource update
        """
        resource = resource_factory()

        assert _get_data_plugin_calls() == 1
        assert _get_pipe_plugin_calls() == 1

        resource['format'] = 'CSV'
        resource['url'] = 'https://example.com/data.csv'

        call_action('resource_update', **resource)

        assert mock_validation.called
        assert _get_data_plugin_calls() == 2
        assert _get_pipe_plugin_calls() == 2

    def test_can_validate_called_on_update_sync_no_validation(
            self, mock_validation, resource_factory):
        _reset_plugin_counter()
        """Plugin must be called 2 times for SYNC mode.
        1. resource before_create on resource create
        2. resource before_update on resource update
        """
        resource = resource_factory(do_not_validate=True)
        assert _get_data_plugin_calls() == 1
        assert _get_pipe_plugin_calls() == 1

        resource['format'] = 'TTF'
        call_action('resource_update', **resource)

        assert _get_data_plugin_calls() == 2
        assert _get_pipe_plugin_calls() == 2
        assert not mock_validation.called


@pytest.mark.usefixtures("clean_db", "validation_setup")
@pytest.mark.ckan_config(settings.ASYNC_UPDATE_KEY, True)
@pytest.mark.ckan_config(settings.ASYNC_CREATE_KEY, True)
@patch(helpers.MOCK_ENQUEUE_JOB)
class TestInterfaceAsync(BaseTestInterfaces):

    def test_can_validate_called_on_create_async(self, mock_validation,
                                                 resource_factory):
        _reset_plugin_counter()
        """Plugin must be called once for ASYNC mode on create
        1. resource after_create
        """
        resource_factory()

        assert _get_data_plugin_calls() == 1
        assert _get_pipe_plugin_calls() == 1

        assert mock_validation.called

    def test_can_validate_called_on_create_async_no_validation(
            self, mock_validation, resource_factory):
        _reset_plugin_counter()
        """Plugin must be called once for ASYNC mode on create
        1. resource after_create
        """
        resource_factory(do_not_validate=True)

        assert _get_data_plugin_calls() == 1
        assert _get_pipe_plugin_calls() == 1

        assert not mock_validation.called

    def test_can_validate_called_on_update_async(self, mock_validation,
                                                 resource_factory):
        _reset_plugin_counter()
        """Plugin must be called 3 times for ASYNC mode.
        1. resource after_create on resource create
        2. resource before_update on resource update
        3. resource after_update on resource update
        """
        resource = resource_factory(format="PDF")

        assert _get_data_plugin_calls() == 1
        assert _get_pipe_plugin_calls() == 1

        resource['format'] = 'CSV'

        call_action('resource_update', context={'defer_commit': True}, **resource)

        assert _get_data_plugin_calls() == 3
        assert _get_pipe_plugin_calls() == 3
        assert mock_validation.called

    def test_can_validate_called_on_update_async_no_validation(
            self, mock_validation, resource_factory):
        _reset_plugin_counter()
        """Plugin must be called 2 times for ASYNC mode.
        1. resource after_create on resource create
        2. resource before_update on resource update
        3. after_update won't be called, because validation is not required (
            format is not supported
        )
        """
        resource = resource_factory(format="PDF")

        assert _get_data_plugin_calls() == 1
        assert _get_pipe_plugin_calls() == 1

        resource['format'] = "TTF"
        call_action('resource_update', **resource)

        assert _get_data_plugin_calls() == 2
        assert _get_pipe_plugin_calls() == 2
        assert not mock_validation.called
