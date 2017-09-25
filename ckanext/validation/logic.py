# encoding: utf-8

import datetime
import logging

import ckan.plugins as plugins
import ckan.lib.uploader as uploader

import ckantoolkit as t

from ckanext.validation.model import Validation
from ckanext.validation.jobs import run_validation_job
from ckanext.validation import settings


log = logging.getLogger(__name__)

# Auth


def auth_resource_validation_run(context, data_dict):
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

    t.enqueue_job(run_validation_job, [resource])


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


def resource_update(context, data_dict):
    '''Update a resource.

    To update a resource you must be authorized to update the dataset that the
    resource belongs to.

    For further parameters see
    :py:func:`~ckan.logic.action.create.resource_create`.

    :param id: the id of the resource to update
    :type id: string

    :returns: the updated resource
    :rtype: string

    '''
    model = context['model']
    id = t.get_or_bust(data_dict, "id")

    if not data_dict.get('url'):
        data_dict['url'] = ''

    resource = model.Resource.get(id)
    context["resource"] = resource
    old_resource_format = resource.format

    if not resource:
        log.debug('Could not find resource %s', id)
        raise t.Objectt.ObjectNotFound(t._('Resource was not found.'))

    t.check_access('resource_update', context, data_dict)
    del context["resource"]

    package_id = resource.package.id
    pkg_dict = t.get_action('package_show')(
        dict(context, return_type='dict'),
        {'id': package_id})

    for n, p in enumerate(pkg_dict['resources']):
        if p['id'] == id:
            break
    else:
        log.error('Could not find resource %s after all', id)
        raise t.Objectt.ObjectNotFound(t._('Resource was not found.'))

    # Persist the datastore_active extra if already present and not provided
    if ('datastore_active' in resource.extras and
            'datastore_active' not in data_dict):
        data_dict['datastore_active'] = resource.extras['datastore_active']

    for plugin in plugins.PluginImplementations(plugins.IResourceController):
        plugin.before_update(context, pkg_dict['resources'][n], data_dict)

    upload = uploader.get_resource_uploader(data_dict)

    if 'mimetype' not in data_dict:
        if hasattr(upload, 'mimetype'):
            data_dict['mimetype'] = upload.mimetype

    if 'size' not in data_dict and 'url_type' in data_dict:
        if hasattr(upload, 'filesize'):
            data_dict['size'] = upload.filesize

    pkg_dict['resources'][n] = data_dict

    try:
        context['defer_commit'] = True
        context['use_cache'] = False
        updated_pkg_dict = t.get_action('package_update')(context, pkg_dict)
        context.pop('defer_commit')
    except t.ValidationError, e:
        try:
            raise t.ValidationError(e.error_dict['resources'][-1])
        except (KeyError, IndexError):
            raise t.ValidationError(e.error_dict)

    upload.upload(id, uploader.get_max_resource_size())

#    raise t.ValidationError({'validation': 'kaput'})

    model.repo.commit()

    resource = t.get_action('resource_show')(context, {'id': id})

    if old_resource_format != resource['format']:
        t.get_action('resource_create_default_resource_views')(
            {'model': context['model'], 'user': context['user'],
             'ignore_auth': True},
            {'package': updated_pkg_dict,
             'resource': resource})

    for plugin in plugins.PluginImplementations(plugins.IResourceController):
        plugin.after_update(context, resource)

    return resource


def resource_create(context, data_dict):
    '''Appends a new resource to a datasets list of resources.

    :param package_id: id of package that the resource should be added to.

    :type package_id: string
    :param url: url of resource
    :type url: string
    :param revision_id: (optional)
    :type revision_id: string
    :param description: (optional)
    :type description: string
    :param format: (optional)
    :type format: string
    :param hash: (optional)
    :type hash: string
    :param name: (optional)
    :type name: string
    :param resource_type: (optional)
    :type resource_type: string
    :param mimetype: (optional)
    :type mimetype: string
    :param mimetype_inner: (optional)
    :type mimetype_inner: string
    :param cache_url: (optional)
    :type cache_url: string
    :param size: (optional)
    :type size: int
    :param created: (optional)
    :type created: iso date string
    :param last_modified: (optional)
    :type last_modified: iso date string
    :param cache_last_updated: (optional)
    :type cache_last_updated: iso date string
    :param upload: (optional)
    :type upload: FieldStorage (optional) needs multipart/form-data

    :returns: the newly created resource
    :rtype: dictionary

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

    if data_dict['format'].lower() == 'csv':
        import json
        from ckanext.validation.jobs import _validate_table
        source = None
        if data_dict.get(u'url_type') == u'upload':
            source = upload.get_path(resource_id)
        if not source:
            source = data_dict[u'url']

        schema = data_dict.get(u'schema')
        if schema and isinstance(schema, basestring):
            schema = json.loads(schema)

        _format = data_dict[u'format'].lower()

        report = _validate_table(source, _format=_format, schema=schema)

        # Hide uploaded files
        for table in report.get(u'tables', []):
            if table[u'source'].startswith(u'/'):
                table[u'source'] = data_dict[u'url']

        if not report['valid']:
            raise t.ValidationError({u'validation': [t._('kaput, here\'s a link to the <a href="/">report</a> or the report: {}.'.format(report))]})
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

