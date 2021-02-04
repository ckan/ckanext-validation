# encoding: utf-8
import json
import six

import tableschema

from ckantoolkit import Invalid, config


# Input validators

def resource_schema_validator(value, context):

    if not value:
        return

    msg = None

    if isinstance(value, six.string_types):

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
    else:
        descriptor = value

    try:
        tableschema.validate(descriptor)
    except tableschema.exceptions.ValidationError as e:
        errors = []
        for error in e.errors:
            errors.append(error.message)
        msg = u'Invalid Table Schema: {}'.format(u', '.join(errors))

    if msg:
        raise Invalid(msg)

    return json.dumps(descriptor)


def validation_options_validator(value, context):
    '''Add default validation options if not already present

    At this point the value should already be a valid JSON string (ie
    `scheming_valid_json_object` has been run).
    '''

    default_options = config.get(
        'ckanext.validation.default_validation_options')

    if default_options:
        default_options = json.loads(default_options)

        provided_options = json.loads(value)

        default_options.update(provided_options)

        value = json.dumps(default_options, indent=None, sort_keys=True)

    return value
