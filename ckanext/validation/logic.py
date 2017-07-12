import ckantoolkit as t

from ckanext.validation.jobs import run_validation_job

# TODO: configurable
SUPPORTED_FORMATS = ['csv', 'xls', 'xlsx']


def resource_validation_run(context, data_dict):
    '''
    Start a validation job against a resource.
    Returns the identifier for the job started.

    TODO: resource formats

    :param resource_id: id of the resource to validate
    :type resource_id: string

    :rtype: string

    '''

    if not data_dict.get('resource_id'):
        raise t.ValidationError({'resource_id': 'Missing value'})

    resource = t.get_action('resource_show')(
        {}, {'id': data_dict['resource_id']})

    # Ensure format is supported
    if not resource.get('format', '').lower() in SUPPORTED_FORMATS:
        raise t.ValidationError(
            {'format': 'Unsupported resource format. Must be one of {}'.format(
                ','.join(SUPPORTED_FORMATS))})

    # Ensure there is a URL or file upload
    if not resource.get('url') and not resource.get('url_type') == 'upload':
        raise t.ValidationError(
            {'url': 'Resource must have a valid URL or an uploaded file'})

    t.enqueue_job(run_validation_job, [resource])
