# encoding: utf-8

import logging
import json
import re
import os

from six import ensure_str
import tempfile
import typing
from datetime import datetime as dt

import requests
from frictionless import Report
from requests.exceptions import RequestException
from six import string_types

from ckan import model, plugins
from ckan.lib import uploader
import ckan.plugins.toolkit as tk

from . import settings as s, jobs
from .interfaces import IDataValidation, IPipeValidation
from .validation_status_helper import ValidationStatusHelper, StatusTypes
from .validators import resource_schema_validator

log = logging.getLogger(__name__)

upload_types: 'list[typing.Any]'
if hasattr(uploader, 'ALLOWED_UPLOAD_TYPES'):
    upload_types = getattr(uploader, 'ALLOWED_UPLOAD_TYPES')
else:
    from werkzeug.datastructures import FileStorage as FlaskFileStorage
    upload_types = [FlaskFileStorage]
    if tk.check_ckan_version(max_version='2.10.0'):
        from cgi import FieldStorage
        upload_types.append(FieldStorage)

ALLOWED_UPLOAD_TYPES: 'tuple[typing.Any]' = tuple(upload_types)


def _get_underlying_file(wrapper):
    if hasattr(wrapper, 'stream'):
        return wrapper.stream
    return wrapper.file


def process_schema_fields(data_dict):
    u'''
    Normalize the different ways of providing the `schema` field

    1. If `schema_upload` is provided and it's a valid file, the contents
        are read into `schema`.
    2. If `schema_url` is provided and looks like a valid URL, it's copied
        to `schema`.
    3. If `schema_json` is present, even if blank or empty, it's stripped of
        leading/trailing whitespace and copied to `schema`.

    All the 3 `schema_*` fields are removed from the data_dict.
    Note that the data_dict still needs to pass validation
    '''

    schema_upload = data_dict.pop(u'schema_upload', None)
    schema_url = data_dict.pop(u'schema_url', None)
    # Distinguish blank field (likely web UI) from absent field (likely API).
    # Absent fields do not overwrite the existing schema,
    # but fields that are present and blank can.
    has_schema_json = u'schema_json' in data_dict
    if has_schema_json:
        schema_json = data_dict.pop(u'schema_json')

    if is_uploaded_file(schema_upload):
        data_dict[u'schema'] = ensure_str(
            _get_underlying_file(schema_upload).read())

    elif schema_url:
        if not tk.h.is_url_valid(schema_url):
            raise tk.ValidationError({u'schema_url': ['Must be a valid URL']})

        try:
            resp = requests.get(schema_url)
            schema = resp.json()
        except (ValueError, RequestException):
            raise tk.ValidationError(
                {u'schema_url': ['Can\'t read a valid schema from url']})

        data_dict[u'schema'] = schema

    elif has_schema_json:
        if isinstance(schema_json, str):
            schema_json = schema_json.strip()
        data_dict[u'schema'] = schema_json

    if not data_dict.get('schema'):
        return data_dict

    try:
        resource_schema_validator(data_dict[u'schema'], {})
    except tk.Invalid:
        raise tk.ValidationError({u'schema': ['Schema is invalid']})

    return data_dict


def validate_resource(context, data_dict, new_resource=False):
    mode = s.get_create_mode(context, data_dict) if new_resource \
        else s.get_update_mode(context, data_dict)
    log.info("Validating %s in %s mode", 'create' if new_resource else 'update', mode)

    assert mode in [s.SYNC_MODE, s.ASYNC_MODE]
    if mode == s.SYNC_MODE:
        run_sync_validation(data_dict)
    else:
        run_async_validation(data_dict)


def run_sync_validation(resource_data):
    """If we are using sync validation (validation on update/create resource)
    We must do it before the actual file upload, because if file is invalid
    we don't want to replace the old one

    Args:
        resource_data (dict): new/updated resource data
    """
    schema = resource_data.get('schema')

    if tk.asbool(resource_data.get('align_default_schema')):
        schema = get_default_schema(resource_data["package_id"])

    if schema and isinstance(schema, string_types):
        # schema = schema if tk.h.is_url_valid(schema) else json.loads(schema)
        if tk.h.is_url_valid(schema):
            r = requests.get(schema)
            schema = r.json()
        else:
            schema = json.loads(schema)

    if not schema:
        resource_id = resource_data.get('id')
        if not resource_id:
            return

        context = {u'ignore_auth': True}
        data_dict = {u'resource_id': resource_id}

        try:
            tk.get_action(u'resource_validation_delete')(context, data_dict)
        except tk.ObjectNotFound:
            pass
        return

    _format = resource_data.get('format', '').lower()
    options = get_resource_validation_options(resource_data)

    new_file = resource_data.get('upload')

    if is_uploaded_file(new_file):
        source = _get_new_file_stream(new_file)
    else:
        if tk.h.is_url_valid(resource_data['url']):
            source = resource_data['url']
        else:
            source = _get_uploaded_resource_path(resource_data)

    report = jobs.validate_table(source,
                                 _format=_format,
                                 schema=schema or None,
                                 **options)

    # Hide uploaded files
    if isinstance(report, Report):
        report = report.to_dict()

    if u'tasks' in report:
        for table in report['tasks']:
            if table['place'].startswith('/'):
                table['place'] = resource_data['url']

    status = StatusTypes.running
    if u'warnings' in report:
        if (report['warnings'] is not True):
            status = StatusTypes.failure
        for index, warning in enumerate(report['warnings']):
            report['warnings'][index] = re.sub(r'Table ".*"', 'Table', warning)

    if (
            status == StatusTypes.error
            or (u'valid' not in report)
            or ('valid' in report and not report['valid'])
    ):
        for table in report.get('tables', []):
            table['place'] = resource_data['url']

        raise tk.ValidationError({u'validation': [report]})
    else:
        # get row count from stats located in tasks array 0
        try:
            _table_count = report['tasks'][0]['stats'].get('rows', 0) > 0
        except (KeyError, TypeError, IndexError):
            _table_count = 0
        resource_data[
            'validation_status'] = StatusTypes.success if _table_count else ""
        resource_data['validation_timestamp'] = str(
            dt.now()) if _table_count else ""
        resource_data['_success_validation'] = True


def _get_uploaded_resource_path(resource_data):
    """Get a path for uploaded resource. Supports a default ResourceUpload and
    ckanext-s3filestore S3ResourceUploader."""
    upload = uploader.get_resource_uploader(resource_data)
    path = None

    if isinstance(upload, uploader.ResourceUpload):
        path = upload.get_path(resource_data['id'])
    else:
        try:
            from ckanext.s3filestore.uploader import S3ResourceUploader
        except Exception:
            return path

        if isinstance(upload, S3ResourceUploader):
            filename = os.path.basename(resource_data["url"])
            key_path = upload.get_path(resource_data["id"], filename)
            path = upload.get_signed_url_to_key(key_path, {
                'ResponseContentDisposition':
                'attachment; filename=' + filename,
            })

    return path


def _get_session(resource_data):
    dataset = tk.get_action('package_show')({
        'user': get_site_user()['name']
    }, {
        'id': resource_data['package_id']
    })

    pass_auth_header = tk.asbool(
        tk.config.get(s.PASS_AUTH_HEADER, s.PASS_AUTH_HEADER_DEFAULT))

    if dataset[u'private'] and pass_auth_header:
        _session = requests.Session()
        _session.headers.update({
            u'Authorization':
            tk.config.get(s.PASS_AUTH_HEADER_VALUE, get_site_user_api_key())
        })

        return _session


def _get_new_file_stream(file):
    if hasattr(file, "file"):
        file = file.file

    # frictionless needs a file on disk, it can't work with in memory file streams :'(
    with tempfile.NamedTemporaryFile(delete=False, mode='wb') as temp_file:
        temp_file.write(file.read())
        temp_file_path = temp_file.name

    file.seek(0)

    return temp_file_path


def run_async_validation(data_dict):
    try:
        tk.get_action(u'resource_validation_run')(
            {u'ignore_auth': True, 'resource': data_dict},
            {u'resource_id': data_dict['id'],
             u'async': True})
    except tk.ValidationError as e:
        log.warning(u'Could not run validation for resource {}: {}'.format(
            data_dict['id'], e))


def is_resource_could_be_validated(context, data_dict):
    """Check if new resource could be validated"""
    for plugin in plugins.PluginImplementations(IDataValidation):
        if not plugin.can_validate(context, data_dict):
            log.debug('Skipping validation for new resource')
            return False

    if not data_dict.get(u'format'):
        log.info("Missing resource format. Skipping validation")
        return False

    res_format = data_dict.get(u'format', u'').lower()
    supportable_format = res_format in s.get_supported_formats()

    if supportable_format and (data_dict.get(u'url_type') == u'upload'
                               or data_dict.get(u'upload')
                               or data_dict.get(u'url')):
        return True

    return False


def get_default_schema(package_id):
    """Dataset could have a default_schema, that could be used
    to validate resource"""

    dataset = model.Package.get(package_id)

    if not dataset:
        return

    return dataset.extras.get(u'default_data_schema')


def is_resource_requires_validation(context, old_resource, new_resource):
    """Compares current resource data with updated resource data to understand
    do we need to re-validate it"""
    res_id = new_resource["id"]
    schema = new_resource.get(u'schema')
    schema_aligned = tk.asbool(new_resource.get('align_default_schema'))

    for plugin in plugins.PluginImplementations(IDataValidation):
        if not plugin.can_validate(context, new_resource):
            log.debug(u"Skipping validation for resource {}".format(res_id))
            return False

    if not new_resource.get(u'format'):
        log.info(u"Missing resource format. Skipping validation")
        return False

    if new_resource.get(u'upload'):
        log.info(u"New resource file. Validation required")
        return True

    if new_resource.get(u'url') != old_resource.get(u'url'):
        log.info(u"New resource url. Validation required")
        return True

    if (schema != old_resource.get(u'schema')) or schema_aligned:
        log.info("Schema has been updated. Validation required")
        return True

    old_format = old_resource.get(u'format', u'').lower()
    new_format = new_resource.get(u'format', u'').lower()
    is_format_changed = new_format != old_format

    if is_format_changed and new_format in s.get_supported_formats():
        log.info("Format has been changed. Validation required")
        return True

    if old_resource.get("validation_options") != new_resource.get("validation_options"):
        log.info("Validation options have been updated. Validation required")
        return True

    return False


def is_api_call():
    controller, action = tk.get_endpoint()

    resource_edit = (controller == "resource" and action == "edit") or (
        controller == "package" and action == "resource_edit"
    )
    resource_create = action == "new_resource"
    package_edit = (controller == "dataset" and action == "edit") or (
        controller == "package" and action == "edit"
    )

    return not (resource_edit or resource_create or package_edit)


def is_dataset(data_dict):
    """Checks if data_dict is dataset dict"""
    return (u'creator_user_id' in data_dict or u'owner_org' in data_dict
            or u'resources' in data_dict
            or data_dict.get(u'type') == u'dataset')


def create_success_validation_job(resource_id):
    """Create a success job after validation passed
    We have to do it, because at the resource creation stage we don't have
    a resource_id, so first we are validating file and if it's valid - we are
    creating resource, and at the `after_create` & `after_update` stage creating
    a success validation record."""
    vsh = ValidationStatusHelper()

    record = vsh.createValidationJob(model.Session, resource_id)
    record = vsh.updateValidationJobStatus(session=model.Session,
                                           resource_id=resource_id,
                                           status=StatusTypes.success,
                                           validationRecord=record)


def get_resource_validation_options(resource_data):
    """Prepares resource validation options by combining the default ones
    and specific ones from `validation_options` field.

    Args:
        resource_data (dict): resource data

    Returns:
        dict: validation options dict
    """
    options = s.get_default_validation_options()
    resource_options = resource_data.get(u'validation_options')

    if resource_options and isinstance(resource_options, string_types):
        resource_options = json.loads(resource_options)

    if resource_options:
        options.update(resource_options)

    return options


def get_site_user():
    context = {'ignore_auth': True}
    site_user_name = tk.get_action('get_site_user')(context, {})
    return tk.get_action('get_site_user')(context, {'id': site_user_name})


def get_site_user_api_key():
    return get_site_user()['apikey']


def is_uploaded_file(upload):
    return isinstance(upload,
                      ALLOWED_UPLOAD_TYPES) and upload.filename


def validation_dictize(validation):
    report = validation.report
    if not isinstance(report, dict):
        report = json.loads(str(report))
    out = {
        'id': validation.id,
        'resource_id': validation.resource_id,
        'status': validation.status,
        'report': report,
        'error': validation.error,
    }
    out['created'] = (validation.created.isoformat()
                      if validation.created else None)
    out['finished'] = (validation.finished.isoformat()
                       if validation.finished else None)

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
