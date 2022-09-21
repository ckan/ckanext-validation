# encoding: utf-8

import logging
import datetime
import json
import re

import requests
from sqlalchemy.orm.exc import NoResultFound
# from goodtables import validate
from frictionless import validate, system, Report

from ckan.model import Session
import ckan.lib.uploader as uploader

import ckantoolkit as t

from ckanext.validation.model import Validation


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
            if dataset['private'] and pass_auth_header:
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
    if schema and isinstance(schema, str):
        if schema.startswith('http'):
            r = requests.get(schema)
            schema = r.json()
        else:
            schema = json.loads(schema)

    _format = resource['format'].lower()

    report = _validate_table(source, _format=_format, schema=schema, **options)

    # Hide uploaded files
    if type(report) == Report:
        report = report.to_dict()
    if 'tables' in report:
        for table in report['tables']:
            if table['source'].startswith('/'):
                table['source'] = resource['url']
    if 'warnings' in report:
        for index, warning in enumerate(report['warnings']):
            report['warnings'][index] = re.sub(r'Table ".*"', 'Table', warning)
    if 'valid' in report and report['valid']:
        validation.status = 'success' if report['valid'] else 'failure'
        validation.report = json.dumps(report)
    else:
        validation.status = 'error'
        validation.report = json.dumps(report)
        if 'tables' in report: 
            validation.error = {
                'message': [str(err) for err in report['tables'][0]['errors']] if len(report['tables'][0]['errors']) > 0 else 'No tables found'}
        else:
            validation.error = {'message': []}
    validation.finished = datetime.datetime.utcnow()

    Session.add(validation)
    Session.commit()

    # Store result status in resource
    t.get_action('resource_patch')(
        {'ignore_auth': True,
         'user': t.get_action('get_site_user')({'ignore_auth': True})['name'],
         '_validation_performed': True},
        {'id': resource['id'],
         'validation_status': validation.status,
         'validation_timestamp': validation.finished.isoformat()})


def _validate_table(source, _format='csv', schema=None, **options):

    # TODO: Search if there is an equivalent way to use a proxy in Frictionless Framework v5
    # http_session = options.pop('http_session', None) or requests.Session()

    # use_proxy = 'ckan.download_proxy' in t.config
    # if use_proxy:
    #     proxy = t.config.get('ckan.download_proxy')
    #     log.debug('Download resource for validation via proxy: %s', proxy)
    #     http_session.proxies.update({'http': proxy, 'https': proxy})

    #report = validate(source, format=_format, schema=schema, http_session=http_session, **options)


    with system.use_context(trusted=True):
        report = validate(source, format=_format, schema=schema, **options)
        log.debug('Validating source: %s', source)

    return report


def _get_site_user_api_key():

    site_user_name = t.get_action('get_site_user')({'ignore_auth': True}, {})
    site_user = t.get_action('get_site_user')(
        {'ignore_auth': True}, {'id': site_user_name})
    return site_user['apikey']
