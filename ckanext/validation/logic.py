# encoding: utf-8

import datetime
import logging
import json
import six

from sqlalchemy.orm.exc import NoResultFound

import ckan.plugins as plugins
import ckan.lib.uploader as uploader

import ckantoolkit as t

from ckanext.validation.model import Validation
from ckanext.validation.interfaces import IDataValidation
from ckanext.validation.jobs import run_validation_job
from ckanext.validation import settings
from ckanext.validation.utils import (
    get_create_mode_from_config,
    get_update_mode_from_config,
    delete_local_uploaded_file,
)


log = logging.getLogger(__name__)


def enqueue_job(*args, **kwargs):
    try:
        return t.enqueue_job(*args, **kwargs)
    except AttributeError:
        from ckanext.rq.jobs import enqueue as enqueue_job_legacy
        return enqueue_job_legacy(*args, **kwargs)


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


def auth_resource_validation_run_batch(context, data_dict):
    '''u Sysadmins only'''
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

    try:
        validation = Session.query(Validation).filter(
            Validation.resource_id == data_dict['resource_id']).one()
    except NoResultFound:
        validation = None

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
        enqueue_job(run_validation_job, [resource])
    else:
        run_validation_job(resource)


@t.side_effect_free
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

    try:
        validation = Session.query(Validation).filter(
            Validation.resource_id == data_dict['resource_id']).one()
    except NoResultFound:
        validation = None

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

    try:
        validation = Session.query(Validation).filter(
            Validation.resource_id == data_dict['resource_id']).one()
    except NoResultFound:
        validation = None

    if not validation:
        raise t.ObjectNotFound(
            'No validation report exists for this resource')

    Session.delete(validation)
    Session.commit()


def resource_validation_run_batch(context, data_dict):
    u'''
    Start asynchronous data validation on the site resources. If no
    options are provided it will run validation on all resources of
    the supported formats (`ckanext.validation.formats`). You can
    specify particular datasets to run the validation on their
    resources. You can also pass arbitrary search parameters to filter
    the selected datasets.

    Only sysadmins are allowed to run this action.

    Examples::

       curl -X POST http://localhost:5001/api/action/resource_validation_run_batch \
            -d '{"dataset_ids": "ec9bfd88-f90a-45ca-b024-adc8854b49bd"}' \
            -H Content-type:application/json \
            -H Authorization:API_KEY

       curl -X POST http://localhost:5001/api/action/resource_validation_run_batch \
            -d '{"dataset_ids": ["passenger-data-2018", "passenger-data-2017]}}' \
            -H Content-type:application/json \
            -H Authorization:API_KEY


       curl -X POST http://localhost:5001/api/action/resource_validation_run_batch \
            -d '{"query": {"fq": "res_format:XLSX"}}' \
            -H Content-type:application/json \
            -H Authorization:API_KEY

    :param dataset_ids: Run data validation on all resources for a
        particular dataset or datasets. Not to be used with ``query``.
    :type dataset_ids: string or list
    :param query: Extra search parameters that will be used for getting
        the datasets to run validation on. It must be a JSON object like
        the one used by the `package_search` API call. Supported fields
        are ``q``, ``fq`` and ``fq_list``. Check the documentation for
        examples. Note that when using this you will have to specify
        the resource formats to target your Not to be used with
        ``dataset_ids``.
    :type query: dict

    :rtype: string



    '''

    t.check_access(u'resource_validation_run_batch', context, data_dict)

    page = 1
    page_size = 100
    count_resources = 0

    dataset_ids = data_dict.get('dataset_ids')
    if isinstance(dataset_ids, six.string_types):
        try:
            dataset_ids = json.loads(dataset_ids)
        except ValueError:
            dataset_ids = [dataset_ids]

    search_params = data_dict.get('query')
    if isinstance(search_params, six.string_types):
        try:
            search_params = json.loads(search_params)
        except ValueError:
            msg = 'Error parsing search parameters: {}'.format(search_params)
            return {'output': msg}

    while True:

        query = _search_datasets(
            page, page_size=page_size,
            dataset_ids=dataset_ids,
            search_params=search_params)

        if page == 1 and query['count'] == 0:
            msg = 'No suitable datasets for validation'
            return {'output': msg}

        if query['results']:
            for dataset in query['results']:

                if not dataset.get('resources'):
                    continue

                for resource in dataset['resources']:

                    if (not resource.get(u'format', u'').lower()
                            in settings.SUPPORTED_FORMATS):
                        continue

                    try:
                        t.get_action(u'resource_validation_run')(
                            {u'ignore_auth': True},
                            {u'resource_id': resource['id'],
                             u'async': True})

                        count_resources += 1

                    except t.ValidationError as e:
                        log.warning(
                            u'Could not run validation for resource %s from dataset %s: %s',
                            resource['id'], dataset['name'], e)

            if len(query['results']) < page_size:
                break

            page += 1
        else:
            break

    msg = 'Done. {} resources sent to the validation queue'.format(
        count_resources)
    log.info(msg)
    return {'output': msg}


def _search_datasets(
        page=1, page_size=100, dataset_ids=None, search_params=None):
    '''
    Perform a query with `package_search` and return the result

    Results can be paginated using the `page` parameter
    '''

    search_data_dict = {
        'q': '',
        'fq': '',
        'fq_list': [],
        'include_private': True,
        'rows': page_size,
        'start': page_size * (page - 1),
    }

    if dataset_ids:

        search_data_dict['q'] = ' OR '.join(
            ['id:{0} OR name:"{0}"'.format(dataset_id)
             for dataset_id in dataset_ids]
        )

    elif search_params:
        _update_search_params(search_data_dict, search_params)
    else:
        _add_default_formats(search_data_dict)

    if not search_data_dict.get('q'):
        search_data_dict['q'] = '*:*'

    query = t.get_action('package_search')({}, search_data_dict)

    return query


def _update_search_params(search_data_dict, user_search_params=None):
    '''
    Update the `package_search` data dict with the user provided parameters

    Supported fields are `q`, `fq` and `fq_list`.

    If the provided JSON object can not be parsed the process stops with
    an error.

    Returns the updated data dict
    '''

    if not user_search_params:
        return search_data_dict

    if user_search_params.get('q'):
        search_data_dict['q'] = user_search_params['q']

    if user_search_params.get('fq'):
        if search_data_dict['fq']:
            search_data_dict['fq'] += ' ' + user_search_params['fq']
        else:
            search_data_dict['fq'] = user_search_params['fq']

    if (user_search_params.get('fq_list') and
            isinstance(user_search_params['fq_list'], list)):
        search_data_dict['fq_list'].extend(user_search_params['fq_list'])


def _add_default_formats(search_data_dict):

    filter_formats = []

    for _format in settings.DEFAULT_SUPPORTED_FORMATS:
        filter_formats.extend([_format, _format.upper()])

    filter_formats_query = ['+res_format:"{0}"'.format(_format)
                            for _format in filter_formats]
    search_data_dict['fq_list'].append(' OR '.join(filter_formats_query))


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
    except t.ValidationError as e:
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

        run_validation = True

        for plugin in plugins.PluginImplementations(IDataValidation):
            if not plugin.can_validate(context, data_dict):
                log.debug('Skipping validation for resource %s', resource_id)
                run_validation = False

        if run_validation:
            is_local_upload = (
                hasattr(upload, 'filename') and
                upload.filename is not None and
                isinstance(upload, uploader.ResourceUpload))
            _run_sync_validation(
                resource_id, local_upload=is_local_upload, new_resource=True)

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


def resource_update(context, data_dict):
    '''Update a resource.

    This is duplicate of the CKAN core resource_update action, with just the
    addition of a synchronous data validation step.

    This is of course not ideal but it's the only way right now to hook
    reliably into the creation process without overcomplicating things.
    Hopefully future versions of CKAN will incorporate more flexible hook
    points that will allow a better approach.

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
        raise t.ObjectNotFound(t._('Resource was not found.'))

    t.check_access('resource_update', context, data_dict)
    del context["resource"]

    package_id = resource.package.id
    pkg_dict = t.get_action('package_show')(dict(context, return_type='dict'),
                                            {'id': package_id})

    for n, p in enumerate(pkg_dict['resources']):
        if p['id'] == id:
            break
    else:
        log.error('Could not find resource %s after all', id)
        raise t.ObjectNotFound(t._('Resource was not found.'))

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
    except t.ValidationError as e:
        try:
            raise t.ValidationError(e.error_dict['resources'][-1])
        except (KeyError, IndexError):
            raise t.ValidationError(e.error_dict)

    upload.upload(id, uploader.get_max_resource_size())

    # Custom code starts

    if get_update_mode_from_config() == u'sync':

        run_validation = True
        for plugin in plugins.PluginImplementations(IDataValidation):
            if not plugin.can_validate(context, data_dict):
                log.debug('Skipping validation for resource %s', id)
                run_validation = False

        if run_validation:
            is_local_upload = (
                hasattr(upload, 'filename') and
                upload.filename is not None and
                isinstance(upload, uploader.ResourceUpload))
            _run_sync_validation(
                id, local_upload=is_local_upload, new_resource=True)

    # Custom code ends

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


def _run_sync_validation(resource_id, local_upload=False, new_resource=True):

    try:
        t.get_action(u'resource_validation_run')(
            {u'ignore_auth': True},
            {u'resource_id': resource_id,
             u'async': False})
    except t.ValidationError as e:
        log.info(u'Could not run validation for resource %s: %s',
                 resource_id, e)
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

        # Delete uploaded file
        if local_upload:
            delete_local_uploaded_file(resource_id)

        if new_resource:
            # Delete resource
            t.get_action(u'resource_delete')(
                {u'ignore_auth': True, 'user': None},
                {u'id': resource_id}
            )

        raise t.ValidationError({
            u'validation': [report]})
