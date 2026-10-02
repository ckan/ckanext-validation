# encoding: utf-8

import logging
import json

from ckan.plugins import toolkit as tk
from six import string_types

from ckanext.validation.jobs import run_validation_job
from ckanext.validation import settings
from ckanext.validation.validation_status_helper import (
    ValidationStatusHelper, ValidationJobAlreadyEnqueued)
from ckanext.validation.utils import validation_dictize

log = logging.getLogger(__name__)


def get_actions():
    validators = (
        resource_validation_run,
        resource_validation_show,
        resource_validation_delete,
        resource_validation_run_batch,
        package_patch,
        resource_show,
    )

    return {"{}".format(func.__name__): func for func in validators}


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

    tk.check_access(u'resource_validation_run', context, data_dict)

    if 'resource' in context:
        resource = context['resource']
        resource_id = resource['id']
    else:
        resource_id = data_dict.get(u'resource_id')
        if not resource_id:
            raise tk.ValidationError({u'resource_id': u'Missing value'})

        resource = tk.get_action(u'resource_show')(context, {u'id': resource_id})
    log.debug("Attempting to validate resource: %s", resource)

    if not resource.get('schema'):
        log.warning("No schema found on %s, cannot validate", resource_id)
        try:
            tk.get_action(u'resource_validation_delete')(context, data_dict)
        except tk.ObjectNotFound:
            pass
        return

    # TODO: limit to sysadmins
    async_job = data_dict.get(u'async', True)

    supported_formats = settings.get_supported_formats()

    # Ensure format is supported
    if not resource.get(u'format', u'').lower() in supported_formats:
        log.error("Unable to run validation for resource: %s", resource)
        raise tk.ValidationError({
            u'format':
            u'Unsupported resource format.'
            u'Must be one of {}'.format(u','.join(supported_formats))
        })

    # Ensure there is a URL or file upload
    if not resource.get(u'url') and not resource.get(u'url_type') == u'upload':
        raise tk.ValidationError(
            {u'url': u'Resource must have a valid URL or an uploaded file'})

    # Check if there was an existing validation for the resource
    try:
        session = context['model'].Session
        ValidationStatusHelper().createValidationJob(session, resource_id)
    except ValidationJobAlreadyEnqueued:
        if async_job:
            log.error(
                "resource_validation_run: ValidationJobAlreadyEnqueued %s",
                data_dict['resource_id'])
            return

    if async_job:
        package_id = resource['package_id']
        enqueue_validation_job(package_id, resource_id)
    else:
        run_validation_job(resource)


def enqueue_validation_job(package_id, resource_id):
    job_title = "run_validation_job: package_id: {} resource: {}".format(
        package_id, resource_id),

    enqueue_args = {
        'fn': run_validation_job,
        'title': job_title,
        'kwargs': {
            'resource': resource_id,
        }
    }

    ttl = 24 * 60 * 60  # 24 hour ttl.
    rq_kwargs = {
        'ttl': ttl, 'failure_ttl': ttl
    }
    enqueue_args['rq_kwargs'] = rq_kwargs

    # Optional variable, if not set, default queue is used
    queue = tk.config.get('ckanext.validation.queue', None)

    if queue:
        enqueue_args['queue'] = queue

    tk.enqueue_job(**enqueue_args)


@tk.side_effect_free
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

    tk.check_access(u'resource_validation_show', context, data_dict)

    if not data_dict.get(u'resource_id'):
        raise tk.ValidationError({u'resource_id': u'Missing value'})

    session = context['model'].Session
    validation = ValidationStatusHelper().getValidationJob(
        session, data_dict['resource_id'])

    if not validation:
        raise tk.ObjectNotFound(
            'No validation report exists for this resource')

    return validation_dictize(validation)


def resource_validation_delete(context, data_dict):
    u'''
    Remove the validation job result for a particular resource.
    It also deletes the underlying Validation object.

    :param resource_id: id of the resource to remove validation from
    :type resource_id: string

    :rtype: None

    '''

    tk.check_access(u'resource_validation_delete', context, data_dict)

    if not data_dict.get(u'resource_id'):
        raise tk.ValidationError({u'resource_id': u'Missing value'})

    session = context['model'].Session
    validation = ValidationStatusHelper().getValidationJob(
        session, data_dict['resource_id'])

    if not validation:
        raise tk.ObjectNotFound(
            'No validation report exists for this resource')

    ValidationStatusHelper().deleteValidationJob(session, validation)


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

    tk.check_access(u'resource_validation_run_batch', context, data_dict)

    page = 1
    page_size = 100
    count_resources = 0

    dataset_ids = data_dict.get('dataset_ids')
    if isinstance(dataset_ids, string_types):
        try:
            dataset_ids = json.loads(dataset_ids)
        except ValueError:
            dataset_ids = [dataset_ids]

    search_params = data_dict.get('query')
    if isinstance(search_params, string_types):
        try:
            search_params = json.loads(search_params)
        except ValueError:
            msg = 'Error parsing search parameters: {}'.format(search_params)
            return {'output': msg}

    while True:

        query = _search_datasets(page,
                                 page_size=page_size,
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
                    res_format = resource.get(u'format', u'').lower()
                    if res_format not in settings.get_supported_formats():
                        continue

                    try:
                        tk.get_action(u'resource_validation_run')(
                            {
                                u'ignore_auth': True
                            }, {
                                u'resource_id': resource['id'],
                                u'async': True
                            })

                        count_resources += 1

                    except tk.ValidationError as e:
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


def _search_datasets(page=1,
                     page_size=100,
                     dataset_ids=None,
                     search_params=None):
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

        search_data_dict['q'] = ' OR '.join([
            'id:{0} OR name:"{0}"'.format(dataset_id)
            for dataset_id in dataset_ids
        ])

    elif search_params:
        _update_search_params(search_data_dict, search_params)
    else:
        _add_default_formats(search_data_dict)

    if not search_data_dict.get('q'):
        search_data_dict['q'] = '*:*'

    query = tk.get_action('package_search')({}, search_data_dict)

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

    if (user_search_params.get('fq_list')
            and isinstance(user_search_params['fq_list'], list)):
        search_data_dict['fq_list'].extend(user_search_params['fq_list'])


def _add_default_formats(search_data_dict):

    filter_formats = []

    for _format in settings.DEFAULT_SUPPORTED_FORMATS:
        filter_formats.extend([_format, _format.upper()])

    filter_formats_query = [
        '+res_format:"{0}"'.format(_format) for _format in filter_formats
    ]
    search_data_dict['fq_list'].append(' OR '.join(filter_formats_query))


@tk.chained_action
def package_patch(original_action, context, data_dict):
    ''' Detect whether resources have been replaced, and if not,
    place a flag in the context accordingly if save flag is not set

    Note: controllers add default context where save is in request params
        'save': 'save' in request.params
    '''
    if 'save' not in context and 'resources' not in data_dict:
        context['save'] = True
    original_action(context, data_dict)


@tk.side_effect_free
@tk.chained_action
def resource_show(next_func, context, data_dict):
    """Throws away _success_validation flag, that we are using to prevent
    multiple validations of resource in different interface methods
    """
    if context.get('ignore_auth'):
        return next_func(context, data_dict)

    data_dict = next_func(context, data_dict)

    data_dict.pop('_success_validation', None)
    return data_dict
