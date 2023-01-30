# encoding: utf-8
from ckan.lib.helpers import url_for_static
from ckan import model
from ckantoolkit import url_for, _, config, asbool, literal, h, request

import json
import re

def get_validation_badge(resource, in_listing=False):

    if in_listing and not asbool(
            config.get('ckanext.validation.show_badges_in_listings', True)):
        return ''

    if not resource.get('validation_status'):
        return ''

    messages = {
        'success': _('Valid data'),
        'failure': _('Invalid data'),
        'error': _('Error during validation'),
        'unknown': _('Data validation unknown'),
    }

    if resource['validation_status'] in ['success', 'failure', 'error']:
        status = resource['validation_status']
    else:
        status = 'unknown'

    validation_url = url_for(
        'validation_read',
        id=resource['package_id'],
        resource_id=resource['id'])

    badge_url = url_for_static(
        '/images/badges/data-{}-flat.svg'.format(status))

    return '''
<a href="{validation_url}" class="validation-badge">
    <img src="{badge_url}" alt="{alt}" title="{title}"/>
</a>'''.format(
        validation_url=validation_url,
        badge_url=badge_url,
        alt=messages[status],
        title=resource.get('validation_timestamp', ''))


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

def validation_dict(validation_json):
    return json.loads(validation_json)

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

def get_package_id_from_resource_url():
    match = re.match("/dataset/(.*)/resource/", request.path)
    if match:
        return model.Package.get(match.group(1)).id

def get_resource_id_from_resource_url():
    match = re.match("/dataset/(.*)/resource/(.*)/edit", request.path)
    if match:
        return model.Resource.get(match.group(2)).id

def use_webassets():
    return int(h.ckan_version().split('.')[1]) >= 9
