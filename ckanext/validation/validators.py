# encoding: utf-8
import json

import tableschema

from ckantoolkit import Invalid


# Input validators

def resource_schema_validator(value, context):

    if not value:
        return

    msg = None

    if isinstance(value, basestring):
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
