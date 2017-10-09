# encoding: utf-8

import datetime
import logging

import ckan.plugins as plugins
import ckan.lib.uploader as uploader

import ckantoolkit as t

from ckanext.validation.model import Validation
from ckanext.validation.jobs import run_validation_job
from ckanext.validation import settings
from ckanext.validation.utils import (
    get_create_mode_from_config,
)


log = logging.getLogger(__name__)

# Auth


def auth_resource_validation_run(context, data_dict):
    if t.check_access(
            u'resource_update', context, {u'id': data_dict[u'resource_id']}):
        return {u'success': True}
    return {u'success': False}


def auth_resource_validation_delete(context, data_dict):
    if t.check_access(
            u'resource_update', context, {u'id': data_dict[u'resource_id']}):
        return {u'success': True}
    return {u'success': False}


@t.auth_allow_anonymous_access
def auth_resource_validation_show(context, data_dict):
    if t.check_access(
            u'resource_show', context, {u'id': data_dict[u'resource_id']}):
        return {u'success': True}
    return {u'success': False}


# Actions


def resource_validation_run(context, data_dict):
    u'''
    Start a validation job against a resource.
    Returns the identifier for the job started.

    Note that the resource format must be one of the supported ones,
    currently CSV or Excel.

    :param resource_id: id of the resource to validate
    :type resource_id: string

    :rtype: string

    '''

    t.check_access(u'resource_validation_run', context, data_dict)

    if not data_dict.get(u'resource_id'):
        raise t.ValidationError({u'resource_id': u'Missing value'})

    resource = t.get_action(u'resource_show')(
        {}, {u'id': data_dict[u'resource_id']})

    # TODO: limit to sysadmins
    async_job = data_dict.get(u'async', True)

    # Ensure format is supported
    if not resource.get(u'format', u'').lower() in settings.SUPPORTED_FORMATS:
        raise t.ValidationError(
            {u'format': u'Unsupported resource format.' +
             u'Must be one of {}'.format(
                u','.join(settings.SUPPORTED_FORMATS))})

    # Ensure there is a URL or file upload
    if not resource.get(u'url') and not resource.get(u'url_type') == u'upload':
        raise t.ValidationError(
            {u'url': u'Resource must have a valid URL or an uploaded file'})

    # Check if there was an existing validation for the resource

    Session = context['model'].Session

    validation = Session.query(Validation).filter(
        Validation.resource_id == data_dict['resource_id']).one_or_none()

    if validation:
        # Reset values
        validation.finished = None
        validation.report = None
        validation.error = None
        validation.created = datetime.datetime.utcnow()
        validation.status = u'created'
    else:
        validation = Validation(resource_id=resource['id'])

    Session.add(validation)
    Session.commit()

    if async_job:
        t.enqueue_job(run_validation_job, [resource])
    else:
        run_validation_job(resource)


def resource_validation_show(context, data_dict):
    u'''
    Display the validation job result for a particular resource.
    Returns a validation object, including the validation report or errors
    and metadata about the validation like the timestamp and current status.

    Validation status can be one of:

    * `created`: The validation job is in the processing queue
    * `running`: Validation is under way
    * `error`: There was an error while performing the validation, eg the file
        could not be downloaded or there was an error reading it
    * `success`: Validation was performed, and no issues were found
    * `failure`: Validation was performed, and there were issues found

    :param resource_id: id of the resource to validate
    :type resource_id: string

    :rtype: dict

    '''

    t.check_access(u'resource_validation_show', context, data_dict)

    if not data_dict.get(u'resource_id'):
        raise t.ValidationError({u'resource_id': u'Missing value'})

    Session = context['model'].Session

    validation = Session.query(Validation).filter(
        Validation.resource_id == data_dict['resource_id']).one_or_none()

    if not validation:
        raise t.ObjectNotFound(
            'No validation report exists for this resource')

    return _validation_dictize(validation)


def resource_validation_delete(context, data_dict):
    u'''
    Remove the validation job result for a particular resource.
    It also deletes the underlying Validation object.

    :param resource_id: id of the resource to remove validation from
    :type resource_id: string

    :rtype: None

    '''

    t.check_access(u'resource_validation_delete', context, data_dict)

    if not data_dict.get(u'resource_id'):
        raise t.ValidationError({u'resource_id': u'Missing value'})

    Session = context['model'].Session

    validation = Session.query(Validation).filter(
        Validation.resource_id == data_dict['resource_id']).one_or_none()

    if not validation:
        raise t.ObjectNotFound(
            'No validation report exists for this resource')

    Session.delete(validation)
    Session.commit()


def _validation_dictize(validation):
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


def resource_create(context, data_dict):
    '''Appends a new resource to a datasets list of resources.

    This is duplicate of the CKAN core resource_create action, with just the
    addition of a synchronous data validation step.

    This is of course not ideal but it's the only way right now to hook
    reliably into the creation process without overcomplicating things.
    Hopefully future versions of CKAN will incorporate more flexible hook
    points that will allow a better approach.

    '''
    model = context['model']

    package_id = t.get_or_bust(data_dict, 'package_id')
    if not data_dict.get('url'):
        data_dict['url'] = ''

    pkg_dict = t.get_action('package_show')(
        dict(context, return_type='dict'),
        {'id': package_id})

    t.check_access('resource_create', context, data_dict)

    for plugin in plugins.PluginImplementations(plugins.IResourceController):
        plugin.before_create(context, data_dict)

    if 'resources' not in pkg_dict:
        pkg_dict['resources'] = []

    upload = uploader.get_resource_uploader(data_dict)

    if 'mimetype' not in data_dict:
        if hasattr(upload, 'mimetype'):
            data_dict['mimetype'] = upload.mimetype

    if 'size' not in data_dict:
        if hasattr(upload, 'filesize'):
            data_dict['size'] = upload.filesize

    pkg_dict['resources'].append(data_dict)

    try:
        context['defer_commit'] = True
        context['use_cache'] = False
        t.get_action('package_update')(context, pkg_dict)
        context.pop('defer_commit')
    except t.ValidationError, e:
        try:
            raise t.ValidationError(e.error_dict['resources'][-1])
        except (KeyError, IndexError):
            raise t.ValidationError(e.error_dict)

    # Get out resource_id resource from model as it will not appear in
    # package_show until after commit
    resource_id = context['package'].resources[-1].id
    upload.upload(resource_id,
                  uploader.get_max_resource_size())

    # Custom code starts

    if get_create_mode_from_config() == u'sync':
        _run_sync_validation(resource_id)

    # Custom code ends

    model.repo.commit()

    #  Run package show again to get out actual last_resource
    updated_pkg_dict = t.get_action('package_show')(
        context, {'id': package_id})
    resource = updated_pkg_dict['resources'][-1]

    #  Add the default views to the new resource
    t.get_action('resource_create_default_resource_views')(
        {'model': context['model'],
         'user': context['user'],
         'ignore_auth': True
         },
        {'resource': resource,
         'package': updated_pkg_dict
         })

    for plugin in plugins.PluginImplementations(plugins.IResourceController):
        plugin.after_create(context, resource)

    return resource


def _run_sync_validation(resource_id):

    try:
        t.get_action(u'resource_validation_run')(
            {u'ignore_auth': True},
            {u'resource_id': resource_id,
             u'async': False})
    except t.ValidationError as e:
        log.info(
            u'Could not run validation for resource {}: {}'.format(
                resource_id, str(e)))
        return

    validation = t.get_action(u'resource_validation_show')(
        {u'ignore_auth': True},
        {u'resource_id': resource_id})

    report = validation['report']

    if not report['valid']:

        # Delete validation object
        t.get_action(u'resource_validation_delete')(
            {u'ignore_auth': True},
            {u'resource_id': resource_id}
        )

        # TODO: delete file upload

        raise t.ValidationError({
            u'validation': [report]})
