# encoding: utf-8
import json

import tableschema
from six import string_types, binary_type

from ckantoolkit import Invalid

from ckanext.validation.settings import get_default_validation_options


def get_validators():
    validators = (
        resource_schema_validator,
        validation_options_validator,
    )

    return {"{}".format(func.__name__): func for func in validators}


# Input validators

def resource_schema_validator(value, context):

    if not value:
        return

    msg = None

    if isinstance(value, dict):
        descriptor = value

    elif isinstance(value, string_types):
        value = str(value)

        if value.lower().startswith('http'):
            return value

        try:
            descriptor = json.loads(str(value))
            if not isinstance(descriptor, dict):
                msg = u'Invalid Table Schema descriptor: {}'.format(value)
                raise Invalid(msg)

        except ValueError as e:
            msg = u'JSON error in Table Schema descriptor: {}'.format(e)
            raise Invalid(msg)

    elif isinstance(value, binary_type):
        try:
            # Decode UTF-8 bytes to Unicode, and convert single quotes
            # to double quotes to make it valid JSON
            decoded_value = value.decode('utf8').replace("'", '"')

            descriptor = json.loads(decoded_value)
            if not isinstance(descriptor, dict):
                msg = u'Invalid Table Schema descriptor: {}'.format(value)
                raise Invalid(msg)
        except ValueError as e:
            msg = u'JSON error in Table Schema descriptor: {}'.format(e)
            raise Invalid(msg)
    else:
        descriptor = value

    try:
        tableschema.validate(descriptor)
    except tableschema.exceptions.ValidationError as e:
        errors = []
        for error in e.errors:
            errors.append(str(error))
        msg = u'Invalid Table Schema: {}'.format(u', '.join(errors))

    if msg:
        raise Invalid(msg)

    return json.dumps(descriptor)


def validation_options_validator(value, context):
    '''Add default validation options if not already present

    At this point the value should already be a valid JSON string (ie
    `scheming_valid_json_object` has been run).
    '''

    default_options = get_default_validation_options()

    if default_options:
        provided_options = json.loads(value)

        default_options.update(provided_options)

        value = json.dumps(default_options, indent=None, sort_keys=True)

    return value
