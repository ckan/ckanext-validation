import os
import logging

from ckan.plugins import PluginImplementations
from ckan.lib.uploader import ResourceUpload
from ckantoolkit import config, asbool

from ckanext.validation.interfaces import IPipeValidation


log = logging.getLogger(__name__)


def get_update_mode_from_config():
    if asbool(
            config.get(u'ckanext.validation.run_on_update_sync', False)):
        return u'sync'
    elif asbool(
            config.get(u'ckanext.validation.run_on_update_async', True)):
        return u'async'
    else:
        return None


def get_create_mode_from_config():
    if asbool(
            config.get(u'ckanext.validation.run_on_create_sync', False)):
        return u'sync'
    elif asbool(
            config.get(u'ckanext.validation.run_on_create_async', True)):
        return u'async'
    else:
        return None


def get_local_upload_path(resource_id):
    u'''
    Returns the local path to an uploaded file give an id

    Note: it does not check if the resource or file actually exists
    '''
    upload = ResourceUpload({u'url': u'foo'})
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
    for observer in PluginImplementations(IPipeValidation):
        try:
            observer.receive_validation_report(validation_report)
        except Exception as ex:
            log.exception(ex)
            # We reraise all exceptions so they are obvious there
            # is something wrong
            raise
