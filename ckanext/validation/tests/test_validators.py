import json

from nose.tools import assert_raises, assert_equals

from ckantoolkit import Invalid

from ckan.tests.helpers import change_config

from ckanext.validation.validators import (
    resource_schema_validator, validation_options_validator
)


class TestResourceSchemaValidator(object):

    def test_resource_schema_none(self):

        schema = ''

        assert resource_schema_validator(schema, {}) is None

    def test_resource_schema_invalid_json_string(self):

        schema = '{a,b}'

        assert_raises(Invalid, resource_schema_validator, schema, {})

    def test_resource_schema_invalid_schema_string(self):

        schema = '{"a": 1}'

        assert_raises(Invalid, resource_schema_validator, schema, {})

    def test_resource_schema_valid_json_not_a_dict_string(self):

        schema = '[a,2]'

        assert_raises(Invalid, resource_schema_validator, schema, {})

    def test_resource_schema_valid_json_empty_string(self):

        schema = '""'

        assert_raises(Invalid, resource_schema_validator, schema, {})

    def test_resource_schema_invalid_schema_object(self):

        schema = {'a': 1}

        with assert_raises(Invalid) as e:
            resource_schema_validator(schema, {})

        assert e.exception.error.startswith(
            'Invalid Table Schema: ' +
            'Descriptor validation error: \'fields\' is a required property')

    def test_resource_schema_valid_schema_object(self):

        schema = {'fields': [{'name': 'longitude'}]}

        value = resource_schema_validator(schema, {})

        assert_equals(value, json.dumps(schema))

    def test_resource_schema_valid_schema_string(self):

        schema = '{"fields": [{"name": "longitude"}]}'

        value = resource_schema_validator(schema, {})

        assert_equals(value, schema)

    def test_resource_schema_valid_schema_url(self):

        schema = 'https://example.com/schema.json'

        value = resource_schema_validator(schema, {})

        assert_equals(value, schema)

    def test_resource_schema_invalid_wrong_url(self):

        schema = '/some/wrong/url/schema.json'

        assert_raises(Invalid, resource_schema_validator, schema, {})


class TestValidationOptionsValidator(object):
    '''
    Note: At the point this validator is run the value should already
        be a valid JSON string (ie `scheming_valid_json_object` has been
        run)
    '''

    def test_no_default_validation_options(self):

        value = '{"headers":3}'

        assert_equals(validation_options_validator(value, {}), value)

    @change_config('ckanext.validation.default_validation_options',
                   '{"delimiter":";"}')
    def test_default_validation_options(self):

        value = '{"headers": 3}'

        assert_equals(
            validation_options_validator(value, {}),
            '{"delimiter": ";", "headers": 3}'
        )

    @change_config('ckanext.validation.default_validation_options',
                   '{"delimiter":";", "headers":2}')
    def test_default_validation_optionsi_does_not_override(self):

        value = '{"headers": 3}'

        assert_equals(
            validation_options_validator(value, {}),
            '{"delimiter": ";", "headers": 3}'
        )
