import os
import logging

from six import string_types, ensure_str

import ckan.plugins as plugins
import ckan.lib.uploader as uploader
from ckan import model

from ckanext.validation.interfaces import IPipeValidation

log = logging.getLogger(__name__)

from . import settings
import ckan.plugins as p
import ckantoolkit as t


def process_schema_fields(data_dict):
    u'''
     Normalize the different ways of providing the `schema` field

     1. If `schema_upload` is provided and it's a valid file, the contents
         are read into `schema`.
     2. If `schema_url` is provided and looks like a valid URL, it's copied
         to `schema`
     3. If `schema_json` is provided, it's copied to `schema`.

     All the 3 `schema_*` fields are removed from the data_dict.
     Note that the data_dict still needs to pass validation
     '''

    schema_upload = data_dict.pop(u'schema_upload', None)
    schema_url = data_dict.pop(u'schema_url', None)
    schema_json = data_dict.pop(u'schema_json', None)

    if isinstance(schema_upload, uploader.ALLOWED_UPLOAD_TYPES):
        data_dict[u'schema'] = ensure_str(
            uploader._get_underlying_file(schema_upload).read())
        if isinstance(data_dict["schema"], (bytes, bytearray)):
            data_dict["schema"] = data_dict["schema"].decode()
    elif schema_url:

        if (not isinstance(schema_url, string_types) or
                not schema_url.lower()[:4] == u'http'):
            raise t.ValidationError({u'schema_url': 'Must be a valid URL'})
        data_dict[u'schema'] = schema_url
    elif schema_json:
        data_dict[u'schema'] = schema_json

    return data_dict

def run_async_validation(resource_id):

    try:
        t.get_action(u'resource_validation_run')(
            {u'ignore_auth': True},
            {u'resource_id': resource_id,
             u'async': True})
    except t.ValidationError as e:
        log.warning(
            u'Could not run validation for resource %s: %s',
                resource_id, e)



def get_default_schema(package_id):
    """Dataset could have a default_schema, that could be used
    to validate resource"""

    dataset = model.Package.get(package_id)

    if not dataset:
        return

    return dataset.extras.get(u'default_data_schema')


def should_remove_unsupported_resource_validation_reports(res_dict):
    if not t.h.asbool(t.config.get('ckanext.validation.clean_validation_reports', False)):
        return False
    return (not res_dict.get('format', u'').lower() in settings.get_supported_formats()
            and (res_dict.get('url_type') == 'upload'
                or not res_dict.get('url_type'))
            and (t.h.asbool(res_dict.get('validation_status', False))
                or t.h.asbool(res_dict.get('extras', {}).get('validation_status', False))))


def remove_unsupported_resource_validation_reports(resource_id):
    """
    Callback to remove unsupported validation reports.
    Controlled by config value: ckanext.validation.clean_validation_reports.
    Double check the resource format. Only supported Validation formats should have validation reports.
    If the resource format is not supported, we should delete the validation reports.
    """
    context = {"ignore_auth": True}
    try:
        res = p.toolkit.get_action('resource_show')(context, {"id": resource_id})
    except t.ObjectNotFound:
        log.error('Resource %s does not exist.', resource_id)
        return

    if should_remove_unsupported_resource_validation_reports(res):
        log.info('Unsupported resource format "%s". Deleting validation reports for resource %s',
            res.get(u'format', u''), res['id'])
        try:
            p.toolkit.get_action('resource_validation_delete')(context, {
                "resource_id": res['id']})
            log.info('Validation reports deleted for resource %s', res['id'])
        except t.ObjectNotFound:
            log.error('Validation reports for resource %s do not exist', res['id'])




def get_local_upload_path(resource_id):
    u'''
    Returns the local path to an uploaded file give an id

    Note: it does not check if the resource or file actually exists
    '''
    upload = uploader.ResourceUpload({u'url': u'foo'})
    return upload.get_path(resource_id)


def delete_local_uploaded_file(resource_id):
    u'''
    Remove and uploaded file and its parent folders (if empty)

    This assumes the default folder structure of:

        {ckan.storage_path}/resources/{uuid[0:3]}/{uuid[3:6}/{uuid[6:]}

    Note: some checks are performed in case a custom uploader class is used,
    but is not guaranteed to work in all circumstances. Please test before!
    '''
    path = get_local_upload_path(resource_id)

    try:
        if os.path.exists(path):
            os.remove(path)

        first_directory = os.path.split(path)[0]
        if first_directory.endswith(u'resources'):
            return
        if os.listdir(first_directory) == []:
            os.rmdir(first_directory)

        second_directory = os.path.split(first_directory)[0]
        if second_directory.endswith(u'resources'):
            return
        if os.listdir(second_directory) == []:
            os.rmdir(second_directory)

    except OSError as e:
        log.warning(u'Error deleting uploaded file: %s', e)


def validation_dictize(validation):
    out = {
        'id': validation.id,
        'resource_id': validation.resource_id,
        'status': validation.status,
        'report': validation.report,
        'error': validation.error,
    }
    out['created'] = (
        validation.created.isoformat() if validation.created else None)
    out['finished'] = (
        validation.finished.isoformat() if validation.finished else None)

    return out


def send_validation_report(validation_report):
    for observer in plugins.PluginImplementations(IPipeValidation):
        try:
            observer.receive_validation_report(validation_report)
        except Exception as ex:
            log.exception(ex)
            # We reraise all exceptions so they are obvious there
            # is something wrong
            raise
