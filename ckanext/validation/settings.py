# encoding: utf-8

from ckantoolkit import config

# TODO: configurable
DEFAULT_SUPPORTED_FORMATS = [u'csv', u'xls', u'xlsx']


SUPPORTED_FORMATS = config.get(
    u'ckanext.validation.formats', DEFAULT_SUPPORTED_FORMATS)
