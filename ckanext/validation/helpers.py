# encoding: utf-8
import json

from six.moves.urllib.parse import urlparse
from six import string_types
from ckantoolkit import url_for, _, config, asbool, literal, h

from ckanext.validation.utils import get_default_schema

def get_helpers():
    validators = (
        get_validation_badge,
        validation_extract_report_from_errors,
        dump_json_value,
        bootstrap_version,
        validation_hide_source,
        is_url_valid
    )

    return {"{}".format(func.__name__): func for func in validators}


def get_validation_badge(resource, in_listing=False):

    # afterDate = config.get('ckanext.validation.show_badges_after_last_modified_date', "")
    # if afterDate and (not resource.get('last_modified')
    #                   or h.date_str_to_datetime(afterDate)
    #                   >= h.date_str_to_datetime(resource['last_modified'])):
    #     return ''

    if in_listing and not asbool(
            config.get('ckanext.validation.show_badges_in_listings', True)):
        return ''

    if not resource.get('validation_status'):
        return ''

    # if not _get_schema_or_default_schema(resource):
    #     return ''

    statuses = {
        'success': _('valid'),
        'failure': _('invalid'),
        'invalid': _('invalid'),
        'error': _('error'),
        'unknown': _('unknown'),
    }

    messages = {
        'success': _('Valid data'),
        'failure': _('Invalid data'),
        'invalid': _('invalid data'),
        'error': _('Error during validation'),
        'unknown': _('Data validation unknown'),
    }

    if resource['validation_status'] in ['success', 'failure', 'invalid', 'error']:
        status = resource['validation_status']
    else:
        status = 'unknown'

    action = 'validation.read'

    validation_url = url_for(
        action,
        id=resource['package_id'],
        resource_id=resource['id'])

    return u'''
<a href="{validation_url}" class="validation-badge" title="{alt} {title}">
    <span class="prefix">{prefix}</span><span class="status {status}">{status_title}</span>
</a>'''.format(
        validation_url=validation_url,
        prefix=_('data'),
        status=status,
        status_title=statuses[status],
        alt=messages[status],
        title=resource.get('validation_timestamp', ''))


def _get_schema_or_default_schema(resource):

    if asbool(resource.get('align_default_schema')):
        schema = get_default_schema(resource['package_id'])
    else:
        schema = resource.get('schema')

    if schema and isinstance(schema, string_types):
        schema = schema if is_url_valid(schema) else json.loads(schema)

    return schema


def validation_extract_report_from_errors(errors):

    report = None
    for error in errors.keys():
        if error == 'validation':
            report = errors[error][0]
            # Remove full path from table source
            if 'tasks' in report:
                source = report['tasks'][0]['place']
                report['tasks'][0]['place'] = source.split('/')[-1]
            elif 'tables' in report:
                source = report['tables'][0]['source']
                report['tables'][0]['source'] = source.split('/')[-1]
            msg = _('''
There are validation issues with this file, please see the
<a {params}>report</a> for details. Once you have resolved the issues,
click the button below to replace the file.''')
            params = [
                'href="#validation-report"',
                'data-module="modal-dialog"',
                'data-module-div="validation-report-dialog"',
            ]
            new_error = literal(msg.format(params=' '.join(params)))
            errors[error] = [new_error]
            break

    return report, errors


def dump_json_value(value, indent=None):
    """
    Returns the object passed serialized as a JSON string.

    :param value: The object to serialize.
    :returns: The serialized object, or the original value if it could not be
        serialized.
    :rtype: string
    """
    try:
        return json.dumps(value, indent=indent, sort_keys=True)
    except (TypeError, ValueError):
        return value


def bootstrap_version():
    if config.get('ckan.base_public_folder') == 'public':
        return '3'
    else:
        return '2'


def validation_hide_source(type):
    """
    Returns True if the given source type must be hidden on form.
    Type is one of: upload, url or json.
    For any unexpected type returns False
    """
    return asbool(config.get(
        "ckanext.validation.form.hide_{}_source".format(type),
    ))


def is_url_valid(url):
    """Basic checks for url validity"""
    if not isinstance(url, string_types):
        return False

    try:
        tokens = urlparse(url)
    except ValueError:
        return False

    return all([getattr(tokens, attr) for attr in ('scheme', 'netloc')])
