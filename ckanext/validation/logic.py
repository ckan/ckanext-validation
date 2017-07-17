# encoding: utf-8

import datetime

import ckantoolkit as t

from ckanext.validation.model import Validation
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
            {u'format': u'Unsupported resource format.' +
             u'Must be one of {}'.format(u','.join(SUPPORTED_FORMATS))})

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

    if not data_dict.get(u'resource_id'):
        raise t.ValidationError({u'resource_id': u'Missing value'})

    Session = context['model'].Session

    validation = Session.query(Validation).filter(
        Validation.resource_id == data_dict['resource_id']).one_or_none()

    if not validation:
        raise t.ObjectNotFound('No validation report exists for this resource')

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
