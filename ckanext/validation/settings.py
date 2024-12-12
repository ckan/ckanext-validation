# encoding: utf-8
import json

import ckantoolkit as tk

from ckantoolkit import config, asbool

try:
    from tabulator.config import PARSERS
except NameError:
    # Point in time list of parsers from v1.53.5 if library Tabulator not loaded
    PARSERS = {
        'csv': 'tabulator.parsers.csv.CSVParser',
        'datapackage': 'tabulator.parsers.datapackage.DataPackageParser',
        'gsheet': 'tabulator.parsers.gsheet.GsheetParser',
        'html': 'tabulator.parsers.html.HTMLTableParser',
        'inline': 'tabulator.parsers.inline.InlineParser',
        'json': 'tabulator.parsers.json.JSONParser',
        'jsonl': 'tabulator.parsers.ndjson.NDJSONParser',
        'ndjson': 'tabulator.parsers.ndjson.NDJSONParser',
        'ods': 'tabulator.parsers.ods.ODSParser',
        'sql': 'tabulator.parsers.sql.SQLParser',
        'tsv': 'tabulator.parsers.tsv.TSVParser',
        'xls': 'tabulator.parsers.xls.XLSParser',
        'xlsx': 'tabulator.parsers.xlsx.XLSXParser',
    }

SUPPORTED_FORMATS_KEY = u"ckanext.validation.formats"
DEFAULT_SUPPORTED_FORMATS = [u'csv', u'xls', u'xlsx']
DEFAULT_VALIDATION_OPTIONS_KEY = "ckanext.validation.default_validation_options"

PASS_AUTH_HEADER = u"ckanext.validation.pass_auth_header"
PASS_AUTH_HEADER_DEFAULT = True

PASS_AUTH_HEADER_VALUE = u"ckanext.validation.pass_auth_header_value"


def get_default_validation_options():
    """Return a default validation options

    Returns:
        dict[str, Any]: validation options dictionary
    """
    default_options = tk.config.get(DEFAULT_VALIDATION_OPTIONS_KEY)
    return json.loads(default_options) if default_options else {}


def get_supported_formats():
    """Returns a list of supported formats to validate.
    We use a tabulator to parse the file contents, so only those formats for
    which a parser exists are supported

    Returns:
        list[str]: supported format list
    """
    supported_formats = [
        _format.lower()
        for _format in tk.aslist(tk.config.get(SUPPORTED_FORMATS_KEY))
    ]

    for _format in supported_formats:
        assert _format in PARSERS, "Format {} is not supported".format(_format)

    return supported_formats or DEFAULT_SUPPORTED_FORMATS



def get_update_mode_from_config():
    if asbool(
            config.get(u'ckanext.validation.run_on_update_sync', False)):
        return u'sync'
    elif asbool(
            config.get(u'ckanext.validation.run_on_update_async', True)):
        return u'async'
    else:
        return None


def get_create_mode_from_config():
    if asbool(
            config.get(u'ckanext.validation.run_on_create_sync', False)):
        return u'sync'
    elif asbool(
            config.get(u'ckanext.validation.run_on_create_async', True)):
        return u'async'
    else:
        return None