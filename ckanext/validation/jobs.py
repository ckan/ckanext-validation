# encoding: utf-8

import logging
import json
import re

import requests
from frictionless import validate, system, Report, Schema, Dialect, Check
from six import string_types

from ckan.model import Session
import ckan.lib.uploader as uploader
import ckan.plugins.toolkit as t

from . import utils
from .redis_helper import RedisHelper
from .validation_status_helper import (ValidationStatusHelper, ValidationJobDoesNotExist,
                                       ValidationJobAlreadyRunning, StatusTypes)

log = logging.getLogger(__name__)


def _ensure_report_dict(report):
    return report.to_dict() if isinstance(report, Report) else report


def run_validation_job(resource):
    vsh = ValidationStatusHelper()
    # handle either a resource dict or just an ID
    # ID is more efficient, as resource dicts can be very large
    if isinstance(resource, string_types):
        log.debug(u'run_validation_job: calling resource_show: %s', resource)
        resource = t.get_action('resource_show')({'ignore_auth': True}, {'id': resource})

    resource_id = resource.get('id')
    if resource_id:
        log.debug(u'Validating resource: %s', resource_id)
    else:
        log.debug(u'Validating resource dict: %s', resource)
    validation_record = None
    try:
        validation_record = vsh.updateValidationJobStatus(Session, resource_id, StatusTypes.running)
    except ValidationJobAlreadyRunning as e:
        log.error("Won't run enqueued job %s as job is already running or in invalid state: %s", resource['id'], e)
        return
    except ValidationJobDoesNotExist:
        validation_record = vsh.createValidationJob(Session, resource['id'])
        validation_record = vsh.updateValidationJobStatus(
            session=Session, resource_id=resource_id,
            status=StatusTypes.running, validationRecord=validation_record)

    options = utils.get_resource_validation_options(resource)

    dataset = t.get_action('package_show')(
        {'ignore_auth': True}, {'id': resource['package_id']})

    source = None
    if resource.get(u'url_type') == u'upload':
        upload = uploader.get_resource_uploader(resource)
        if isinstance(upload, uploader.ResourceUpload):
            source = upload.get_path(resource[u'id'])
        else:
            # Upload is not the default implementation (ie it's a cloud storage
            # implementation)
            pass_auth_header = t.asbool(
                t.config.get(u'ckanext.validation.pass_auth_header', True))
            if dataset[u'private'] and pass_auth_header:
                s = requests.Session()
                s.headers.update({
                    u'Authorization': t.config.get(
                        u'ckanext.validation.pass_auth_header_value',
                        utils.get_site_user_api_key())
                })

                options[u'http_session'] = s

    if not source:
        source = resource[u'url']

    schema = resource.get(u'schema')
    if schema and isinstance(schema, string_types):
        if schema.startswith('http'):
            r = requests.get(schema)
            schema = r.json()
        else:
            schema = json.loads(schema)

    _format = resource[u'format'].lower()

    report = _ensure_report_dict(validate_table(source, _format=_format, schema=schema, **options))

    if 'tasks' in report:
        for table in report['tasks']:
            if table['place'].startswith('/'):
                table['place'] = resource['url']

    error_payload = None
    if 'warnings' in report:
        for index, warning in enumerate(report['warnings']):
            report['warnings'][index] = re.sub(r'Table ".*"', 'Table', warning)

    if not contains_major_error(report) and u'valid' in report:
        if report[u'valid']:
            status = StatusTypes.success
        else:
            status = StatusTypes.failure
    else:
        status = StatusTypes.error
        # report['errors'] not used anymore, is now inside tasks.
        if 'tasks' in report and 'errors' in report['tasks'][0]:
            error_payload = {'message': [str(err) for err in report['tasks'][0]['errors']]}
        else:
            error_payload = {'message': ['Errors validating the data']}

    validation_record = vsh.updateValidationJobStatus(Session, resource['id'], status, json.dumps(report), error_payload, validation_record)

    # Store result status, without triggering another round of validation.
    RedisHelper().put(resource_id, 'True', 600)
    t.get_action('resource_patch')(
        {'ignore_auth': True,
         'user': t.get_action('get_site_user')({'ignore_auth': True})['name']},
        {'id': resource['id'],
         'validation_status': validation_record.status,
         'validation_timestamp': validation_record.finished.isoformat()})
    utils.send_validation_report(utils.validation_dictize(validation_record))


def contains_major_error(data):
    # https://github.com/frictionlessdata/frictionless-py/blob/v5.18.0/frictionless/errors/resource.py
    error_types = {"resource-error", "source-error", "scheme-error", "format-error", "encoding-error", "compression-error"}

    # Safely get tasks
    tasks = data.get("tasks", [])

    for task in tasks:
        errors = task.get("errors", [])
        for error in errors:
            if error.get("type") in error_types:
                return True

    return False


def _report_has_encoding_error(report):
    report = _ensure_report_dict(report)
    if 'tasks' not in report:
        return False
    for task in report['tasks']:
        if task['errors'] and task['errors'][0]['type'] == 'encoding-error':
            return True
    return False


def validate_table(source, _format=u'csv', schema=None, **options):

    # This option is needed to allow Frictionless Framework to validate absolute paths
    frictionless_context = {'trusted': True}
    http_session = options.pop('http_session', None) or requests.Session()

    proxy = t.config.get('ckan.download_proxy', None)
    if proxy is not None:
        log.debug(u'Download resource for validation via proxy: %s', proxy)
        http_session.proxies.update({'http': proxy, 'https': proxy})

    frictionless_context['http_session'] = http_session
    resource_schema = Schema.from_descriptor(schema) if schema else None

    # Goodtable's conversion to dialect for backwards compatability
    if any(options.get(key) for key in ['headers', 'skip_rows', 'delimiter']):
        dialect_descriptor = options.get('dialect', {})

        if options.get('headers'):
            dialect_descriptor["header"] = True
            dialect_descriptor["headerRows"] = [options['headers']]
            options.pop('headers', None)
        if options.get('skip_rows') and options.get('skip_rows')[0]:
            dialect_descriptor["commentChar"] = str(options['skip_rows'][0])
            options.pop('skip_rows', None)
        if options.get('delimiter'):
            dialect_descriptor["csv"] = {"delimiter": str(options['delimiter'])}
            options.pop('delimiter', None)
        options['dialect'] = dialect_descriptor

    # Load the Resource Dialect as described in https://framework.frictionlessdata.io/docs/framework/Dialect.html
    if 'dialect' in options:
        dialect = Dialect.from_descriptor(options['dialect'])
        options['dialect'] = dialect

    # Load the list of checks and its parameters declaratively as in https://framework.frictionlessdata.io/docs/checks/table.html
    if 'checks' in options:
        checklist = [Check.from_descriptor(c) for c in options['checks']]
        options['checks'] = checklist

    with system.use_context(**frictionless_context):
        log.debug(u'Validating source: %s', source)
        report = validate(source, format=_format, schema=resource_schema, **options)
        if _report_has_encoding_error(report):
            log.warn(u'Default encoding failed, attempting ISO-8859-1')
            fallback_report = validate(source, format=_format, encoding='iso-8859-1', schema=resource_schema, **options)
            if not _report_has_encoding_error(fallback_report):
                report = fallback_report

    return report
