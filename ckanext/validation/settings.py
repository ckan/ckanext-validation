# encoding: utf-8
import json

import ckan.plugins as plugins
import ckan.plugins.toolkit as tk

from ckanext.validation.interfaces import IDataValidation

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

SYNC_MODE = u"sync"
ASYNC_MODE = u"async"
SUPPORTED_MODES = [SYNC_MODE, ASYNC_MODE]

ASYNC_UPDATE_KEY = "ckanext.validation.run_on_update_async"
ASYNC_CREATE_KEY = "ckanext.validation.run_on_create_async"

CREATE_MODE = u"ckanext.validation.default_create_mode"
UPDATE_MODE = u"ckanext.validation.default_update_mode"
DEFAULT_CREATE_MODE = ASYNC_MODE
DEFAULT_UPDATE_MODE = ASYNC_MODE

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


def get_update_mode(context, resource_data):
    is_async = tk.asbool(tk.config.get(ASYNC_UPDATE_KEY))

    mode = ASYNC_MODE if is_async else SYNC_MODE

    for plugin in plugins.PluginImplementations(IDataValidation):
        mode = plugin.set_update_mode(context, resource_data, mode)

    assert mode in SUPPORTED_MODES, u"Mode '{}' is not supported".format(
        mode)

    return mode


def get_create_mode(context, resource_data):
    is_async = tk.asbool(tk.config.get(ASYNC_CREATE_KEY))

    mode = ASYNC_MODE if is_async else SYNC_MODE

    for plugin in plugins.PluginImplementations(IDataValidation):
        mode = plugin.set_create_mode(context, resource_data, mode)

    assert mode in SUPPORTED_MODES, u"Mode '{}' is not supported".format(
        mode)

    return mode
