# encoding: utf-8

import logging
import datetime
import json
import re

import requests
from sqlalchemy.orm.exc import NoResultFound
from frictionless import system, Resource, Package, Report, Schema, Dialect, Check, Checklist, Detector

from ckan.model import Session
import ckan.lib.uploader as uploader

import ckantoolkit as t

from ckanext.validation.model import Validation
from ckanext.validation.utils import get_update_mode_from_config


log = logging.getLogger(__name__)


def run_validation_job(resource):

    log.debug('Validating resource %s', resource['id'])

    try:
        validation = Session.query(Validation).filter(
            Validation.resource_id == resource['id']).one()
    except NoResultFound:
        validation = None

    if not validation:
        validation = Validation(resource_id=resource['id'])

    validation.status = 'running'
    Session.add(validation)
    Session.commit()

    options = t.config.get(
        'ckanext.validation.default_validation_options')
    if options:
        options = json.loads(options)
    else:
        options = {}

    resource_options = resource.get('validation_options')
    if resource_options and isinstance(resource_options, str):
        resource_options = json.loads(resource_options)
    if resource_options:
        options.update(resource_options)

    dataset = t.get_action('package_show')(
        {'ignore_auth': True}, {'id': resource['package_id']})

    source = None
    if resource.get('url_type') == 'upload':
        upload = uploader.get_resource_uploader(resource)
        if isinstance(upload, uploader.ResourceUpload):
            source = upload.get_path(resource['id'])
        else:
            # Upload is not the default implementation (ie it's a cloud storage
            # implementation)
            pass_auth_header = t.asbool(
                t.config.get('ckanext.validation.pass_auth_header', True))
            if pass_auth_header:
                s = requests.Session()
                s.headers.update({
                    'Authorization': t.config.get(
                        'ckanext.validation.pass_auth_header_value',
                        _get_site_user_api_key())
                })

                options['http_session'] = s

    if not source:
        source = resource['url']

    schema = resource.get('schema')
    if schema:
        if isinstance(schema, str):
            if schema.startswith('http'):
                r = requests.get(schema)
                schema = r.json()
            schema = json.loads(schema)

    _format = resource['format'].lower()

    if schema and 'foreignKeys' in schema:
        reference_resources = _prepare_foreign_keys(dataset, schema)
    else:
        reference_resources=[]

    report = _validate_table(source, reference_resources=reference_resources, _format=_format, schema=schema, **options)

    # Hide uploaded files
    if type(report) == Report:
        report = report.to_dict()

    if 'tasks' in report:
        for table in report['tasks']:
            if table['place'].startswith('/'):
                table['place'] = resource['url']
    if 'warnings' in report:
        validation.status = 'error'
        for index, warning in enumerate(report['warnings']):
            report['warnings'][index] = re.sub(r'Table ".*"', 'Table', warning)
    if 'valid' in report:
        validation.status = 'success' if report['valid'] else 'failure'
        validation.report = json.dumps(report)
    else:
        validation.report = json.dumps(report)
        if 'errors' in report and report['errors']: 
            validation.status = 'error'
            validation.error = {
                'message': [str(err) for err in report['errors']]}
        else:
            validation.error = {'message': ['Errors validating the data']}
    validation.finished = datetime.datetime.utcnow()

    Session.add(validation)
    Session.commit()

    # Store result status in resource
    data_dict = {
        'id': resource['id'],
        'validation_status': validation.status,
        'validation_timestamp': validation.finished.isoformat(),
    }

    if get_update_mode_from_config() == 'sync':
        data_dict['_skip_next_validation'] = True,

    patch_context = {
        'ignore_auth': True,
        'user': t.get_action('get_site_user')({'ignore_auth': True})['name'],
        '_validation_performed': True
    }
    t.get_action('resource_patch')(patch_context, data_dict)




def _validate_table(source, _format='csv', schema=None, reference_resources=[], **options):

    # This option is needed to allow Frictionless Framework to validate absolute paths
    frictionless_context = { 'trusted': True }
    http_session = options.pop('http_session', None) or requests.Session()
    use_proxy = 'ckan.download_proxy' in t.config

    if use_proxy:
        proxy = t.config.get('ckan.download_proxy')
        log.debug('Download resource for validation via proxy: %s', proxy)
        http_session.proxies.update({'http': proxy, 'https': proxy})

    frictionless_context['http_session'] = http_session
    resource_schema = Schema.from_descriptor(schema) if schema else None

    # Load the Resource Dialect as described in https://framework.frictionlessdata.io/docs/framework/dialect.html
    if 'dialect' in options:
        dialect = Dialect.from_descriptor(options['dialect'])
        options['dialect'] = dialect

    # Load the list of checks and parameters declaratively as in https://framework.frictionlessdata.io/docs/checks/table.html
    if 'checks' in options:
        checklist = Checklist(checks = [Check.from_descriptor(c) for c in options.pop('checks')])
    else:
        # Note that it's very important to initialise Checklist with NOTHING and not None if there are no checks declared
        checklist = Checklist()
    if 'pick_errors' in options:
        checklist.pick_errors = options.pop('pick_errors', None)
    if 'skip_errors' in options:
        checklist.skip_errors = options.pop('skip_errors', None)

    # remove limit_errors and limit_rows
    limit_errors = options.pop('limit_errors', None)
    limit_rows = options.pop('limit_rows', None)

    with system.use_context(**frictionless_context):
        # load source as frictionless Resource
        if resource_schema:
            # with schema
            resource = Resource(path=source, format=_format, schema=resource_schema, **options)
        else:
            # without schema
            resource = Resource(path=source, format=_format, **options)

        # add resource to a frictionless Package
        package = Package(resources=[resource])

        # if foreign keys are defined, we need to add the referenced resource(s) to the package
        for reference in reference_resources:
            referenced_resource = Resource(**reference)
            package.add_resource(referenced_resource)

        # report = validate(package, pick_errors=pick_errors, skip_errors=skip_errors, limit_errors=limit_errors)
        report = package.validate(checklist=checklist, limit_errors=limit_errors, limit_rows=limit_rows)

    return report


def _load_if_json(value):
    try:
        json_object = json.loads(value)
    except ValueError as e:
        return None
    return json_object

def _prepare_foreign_keys(dataset, schema):
    referenced_resources = []

    for foreign_key in schema.get('foreignKeys', {}):
        log.debug(f'Prepping Foreign Key resources: {foreign_key}')

        if foreign_key['reference']['resource'] == '':
            continue

        foreign_key_resource = None
        foreign_key_format = 'json'
        if foreign_key['reference']['resource'].startswith('http'):
            log.debug(f"Foreign Key resource is at url: {foreign_key['reference']['resource']}")

            foreign_key_resource = foreign_key['reference']['resource']
        if json_object := _load_if_json(foreign_key['reference']['resource']):
            log.debug(f'Foreign Key resource is a json object with keys: {json_object.keys()}')

            foreign_key_resource = json_object
        else:
            log.debug('Foreign Key resource is (presumably) a resource in this dataset.')

            # get the available resources in this dataset
            dataset_resources = [{r.get('resource_type'): {'url':r.get('url'), 'format': r.get('format')}} for r in dataset['resources']]
            dataset_resources = {k:v for list_item in dataset_resources for (k,v) in list_item.items()}

            # check foreign key resource is in the dataset and get the url
            # if it turns out it isn't we will raise an exception
            if foreign_key['reference']['resource'] in dataset_resources.keys():
                foreign_key_resource = dataset_resources[foreign_key['reference']['resource']]['url']
                foreign_key_format = dataset_resources[foreign_key['reference']['resource']]['format'].lower()
            else:
                raise t.ValidationError(
                    {'foreignKey': 'Foreign key reference does not exist.' +
                    'Must be a url, json object or a resource in this dataset.'})
        
        referenced_resources.append({'name': foreign_key['reference']['resource'], 'path': foreign_key_resource, 'format': foreign_key_format})

    log.debug('Foreign key resources required: ' + str(referenced_resources))
    return referenced_resources

def _get_site_user_api_key():

    site_user_name = t.get_action('get_site_user')({'ignore_auth': True}, {})
    site_user = t.get_action('get_site_user')(
        {'ignore_auth': True}, {'id': site_user_name})
    return site_user['apikey']
