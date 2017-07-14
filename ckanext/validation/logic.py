# encoding: utf-8

import ckantoolkit as t

from ckanext.validation.jobs import run_validation_job

# TODO: configurable
SUPPORTED_FORMATS = [u'csv', u'xls', u'xlsx']


def resource_validation_run(context, data_dict):
    u'''
    Start a validation job against a resource.
    Returns the identifier for the job started.

    TODO: resource formats

    :param resource_id: id of the resource to validate
    :type resource_id: string

    :rtype: string

    '''

    if not data_dict.get(u'resource_id'):
        raise t.ValidationError({u'resource_id': u'Missing value'})

    resource = t.get_action(u'resource_show')(
        {}, {u'id': data_dict[u'resource_id']})

    # Ensure format is supported
    if not resource.get(u'format', u'').lower() in SUPPORTED_FORMATS:
        raise t.ValidationError(
            {u'format': u'Unsupported resource format. Must be one of {}'.format(
                u','.join(SUPPORTED_FORMATS))})

    # Ensure there is a URL or file upload
    if not resource.get(u'url') and not resource.get(u'url_type') == u'upload':
        raise t.ValidationError(
            {u'url': u'Resource must have a valid URL or an uploaded file'})

    t.enqueue_job(run_validation_job, [resource])
