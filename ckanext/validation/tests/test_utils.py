# encoding: utf-8

import io
import json
import pytest

from ckan.tests.helpers import change_config

from ckanext.validation import settings as s, utils

from .helpers import MockFileStorage, SCHEMA


class TestConfigValidationMode(object):

    def test_config_defaults(self):

        assert s.get_update_mode({}, {}) == s.SYNC_MODE
        assert s.get_create_mode({}, {}) == s.SYNC_MODE

    @change_config(s.ASYNC_CREATE_KEY, True)
    def test_set_async_as_default_create_mode(self):

        assert s.get_create_mode({}, {}) == s.ASYNC_MODE

    @change_config(s.ASYNC_UPDATE_KEY, True)
    def test_set_async_as_default_update_mode(self):

        assert s.get_update_mode({}, {}) == s.ASYNC_MODE

    @change_config(s.ASYNC_CREATE_KEY, False)
    def test_set_sync_as_default_create_mode(self):

        assert s.get_create_mode({}, {}) == s.SYNC_MODE

    @change_config(s.ASYNC_UPDATE_KEY, False)
    def test_set_sync_as_default_update_mode(self):

        assert s.get_update_mode({}, {}) == s.SYNC_MODE

    @change_config(s.ASYNC_CREATE_KEY, False)
    @change_config(s.ASYNC_UPDATE_KEY, False)
    def test_set_sync_as_default_both_create_and_update(self):

        assert s.get_create_mode({}, {}) == s.SYNC_MODE
        assert s.get_update_mode({}, {}) == s.SYNC_MODE


class TestConfigSupportedFormats(object):

    def test_default_supported_formats(self):
        assert s.DEFAULT_SUPPORTED_FORMATS == s.get_supported_formats()

    @change_config(s.SUPPORTED_FORMATS_KEY, "")
    def test_empty_supported_formats(self):
        assert s.DEFAULT_SUPPORTED_FORMATS == s.get_supported_formats()

    @change_config(s.SUPPORTED_FORMATS_KEY, "ttf")
    def test_set_unsupported_format(self):
        with pytest.raises(AssertionError, match="Format ttf is not supported"):
            s.get_supported_formats()

    @change_config(s.SUPPORTED_FORMATS_KEY, "csv xlsx")
    def test_set_supported_formats(self):
        assert s.get_supported_formats() == ["csv", "xlsx"]


def _assert_schema_inputs_cleared(data_dict):
    assert 'schema_upload' not in data_dict
    assert 'schema_url' not in data_dict
    assert 'schema_json' not in data_dict


@pytest.mark.usefixtures("with_plugins")
class TestProcessingSchemaFields(object):

    schema_url = 'https://github.com/qld-gov-au/ckanext-validation/raw/refs/heads/master/test/fixtures/test_schema.json'
    mock_schema_json = '{"fields": [{"type": "integer", "name": "foo", "format": "default"}]}'
    mock_schema = '{"fields": [{"type": "string", "name": "baz", "format": "default"}]}'

    def test_schema_upload_populates_schema_first(self):
        data_dict = {
            'schema_upload': MockFileStorage(io.StringIO(json.dumps(SCHEMA)), "mock-schema-upload"),
            'schema_url': self.schema_url,
            'schema_json': self.mock_schema_json,
            'schema': self.mock_schema
        }

        result = utils.process_schema_fields(data_dict)
        assert json.loads(result['schema']) == SCHEMA
        _assert_schema_inputs_cleared(data_dict)

    def test_schema_url_populates_schema_second(self):
        data_dict = {
            'schema_upload': None,
            'schema_url': self.schema_url,
            'schema_json': self.mock_schema_json,
            'schema': self.mock_schema
        }

        result = utils.process_schema_fields(data_dict)
        assert result['schema'] == {"fields": [{"name": "field1", "type": "string"}, {"name": "field2", "type": "string"}]}
        _assert_schema_inputs_cleared(data_dict)

    def test_schema_json_populates_schema_third(self):
        data_dict = {
            'schema_upload': None,
            'schema_url': None,
            'schema_json': self.mock_schema_json,
            'schema': self.mock_schema
        }

        result = utils.process_schema_fields(data_dict)
        assert result['schema'] == self.mock_schema_json
        _assert_schema_inputs_cleared(data_dict)

    def test_schema_is_retained_without_other_fields(self):
        data_dict = {
            'schema': self.mock_schema
        }

        result = utils.process_schema_fields(data_dict)
        assert result['schema'] == self.mock_schema
        _assert_schema_inputs_cleared(data_dict)

    def test_schema_is_overwritten_by_empty_json_field(self):
        data_dict = {
            'schema_json': ' ',
            'schema': self.mock_schema
        }

        result = utils.process_schema_fields(data_dict)
        assert not result['schema']
        _assert_schema_inputs_cleared(data_dict)
