# encoding: utf-8

import logging
import datetime
import json
import re

import requests
from sqlalchemy.orm.exc import NoResultFound
from goodtables import validate

from ckan.model import Session
import ckan.lib.uploader as uploader

import ckantoolkit as t
from ckantoolkit import config

from ckanext.validation.model import Validation
import os
import errno


log = logging.getLogger(__name__)


def run_validation_job(resource):
    log.debug(resource)
    log.debug(u'Validating resource {}'.format(resource['id']))

    try:
        validation = Session.query(Validation).filter(
            Validation.resource_id == resource['id']).one()
    except NoResultFound:
        validation = None

    if not validation:
        validation = Validation(resource_id=resource['id'])

    validation.status = u'running'
    Session.add(validation)
    Session.commit()

    source = None
    if resource.get(u'url_type') == u'upload':
        upload = uploader.get_resource_uploader(resource)
        if isinstance(upload, uploader.ResourceUpload):
            source = upload.get_path(resource[u'id'])
    if not source:
        source = resource[u'url']

    schema = resource.get(u'schema')
    if schema and isinstance(schema, basestring):
        if schema.startswith('http'):
            r = requests.get(schema)
            schema = r.json()
        else:
            schema = json.loads(schema)

    options = resource.get(u'validation_options')
    if options and isinstance(options, basestring):
        options = json.loads(options)
    if not isinstance(options, dict):
        options = {}

    _format = resource[u'format'].lower()

    report = _validate_table(source, _format=_format, schema=schema, **options)

    # Hide uploaded files
    for table in report.get('tables', []):
        if table['source'].startswith('/'):
            table['source'] = resource['url']
    for index, warning in enumerate(report.get('warnings', [])):
        report['warnings'][index] = re.sub(r'Table ".*"', 'Table', warning)

    if report['table-count'] > 0:
        validation.status = u'success' if report[u'valid'] else u'failure'
        validation.report = report
    else:
        validation.status = u'error'
        validation.error = {
            'message': '\n'.join(report['warnings']) or u'No tables found'}
    validation.finished = datetime.datetime.utcnow()

    Session.add(validation)
    Session.commit()
    # Push to Logstash folder
    if report[u'valid']:
        url = resource.get('url')
        resource_name = filename_extractor(url)
        package_id = resource.get('package_id')
        log.debug('Saving file for data pipeline....')
        _push_file_to_logstash_folder(source, resource_name, package_id)
    # Store result status in resource
    t.get_action('resource_patch')(
        {'ignore_auth': True,
         'user': t.get_action('get_site_user')({'ignore_auth': True})['name']},
        {'id': resource['id'],
         'validation_status': validation.status,
         'validation_timestamp': validation.finished.isoformat()})


def _validate_table(source, _format=u'csv', schema=None, **options):

    report = validate(source, format=_format, schema=schema,**options)

    log.debug(u'Validating source: {}'.format(source))
   
    return report

def _push_file_to_logstash_folder(_file, _file_name, _dataset_id):
    storage_path=config.get('ckan.storage_path')
    try:
        result = res = t.get_action('package_show')({'ignore_auth': True,
            'user': t.get_action('get_site_user')({'ignore_auth': True})['name']},{'id':_dataset_id})
        package_name = result.get('name')
    except ValueError as e:
        log.debug(e)

    # Create the directory if it didn't exist
    extra_path = os.path.join(storage_path, 'storage', package_name)
    full_path = os.path.join(extra_path,_file_name)
    if not os.path.exists(extra_path):
        try:
            os.makedirs(extra_path)
        except OSError as exc:
            if exc.errno != errno.EEXIST:
                raise

    f = open(_file, 'r')
    w = open(full_path,'w')
    for lines in f:
        w.write(lines)
    w.close()
    f.close()
    log.debug('File saved to %s' % full_path)

"""
filename_extractor - extracts the file extension from the resource url.
This becomes necessary because the name of the resource could be anything.
"""
def filename_extractor(path):
    path_arr = path.split('/')
    path_length = len(path_arr)
    return path_arr[path_length - 1]