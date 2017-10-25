import __builtin__ as builtins
import cgi
import functools
import mock

from pyfakefs import fake_filesystem

import ckan.lib.uploader
from ckan.tests.helpers import change_config


INVALID_CSV = '''a,b,c,d
1,2,3
'''

VALID_CSV = '''a,b,c,d
1,2,3,4
'''

VALID_REPORT = {
    'error-count': 0,
    'table-count': 1,
    'tables': [
        {
            'error-count': 0,
            'errors': [],
            'headers': [
                'name',
                'ward',
                'party',
                'other'
            ],
            'row-count': 79,
            'source': 'http://example.com/valid.csv',
            'time': 0.007,
            'valid': True
        }
    ],
    'time': 0.009,
    'valid': True,
    'warnings': []
}


INVALID_REPORT = {
    'error-count': 2,
    'table-count': 1,
    'tables': [
        {
            'error-count': 2,
            'errors': [
                {
                    'code': 'blank-header',
                    'column-number': 3,
                    'message': 'Header in column 3 is blank',
                    'row': None,
                    'row-number': None
                },
                {
                    'code': 'duplicate-header',
                    'column-number': 4,
                    'message': 'Header in column 4 is duplicated to ...',
                    'row': None,
                    'row-number': None
                },
            ],
            'headers': [
                'name',
                'ward',
                'party',
                'other'
            ],
            'row-count': 79,
            'source': 'http://example.com/valid.csv',
            'time': 0.007,
            'valid': False
        }
    ],
    'time': 0.009,
    'valid': False,
    'warnings': []
}


ERROR_REPORT = {
    'error-count': 0,
    'table-count': 0,
    'warnings': ['Some warning'],
}


VALID_REPORT_LOCAL_FILE = {
    'error-count': 0,
    'table-count': 1,
    'tables': [
        {
            'error-count': 0,
            'errors': [],
            'headers': [
                'name',
                'ward',
                'party',
                'other'
            ],
            'row-count': 79,
            'source': '/data/resources/31f/d4c/1e-9c82-424b-b78b-48cd08db6e64',
            'time': 0.007,
            'valid': True
        }
    ],
    'time': 0.009,
    'valid': True,
    'warnings': []
}


real_open = open
_fs = fake_filesystem.FakeFilesystem()
_mock_os = fake_filesystem.FakeOsModule(_fs)
_mock_file_open = fake_filesystem.FakeFileOpen(_fs)


def _mock_open_if_open_fails(*args, **kwargs):
    try:
        return real_open(*args, **kwargs)
    except (OSError, IOError):
        return _mock_file_open(*args, **kwargs)


def mock_uploads(func):
    @change_config('ckan.storage_path', '/doesnt_exist')
    @mock.patch.object(ckan.lib.uploader, 'os', _mock_os)
    @mock.patch.object(builtins, 'open',
                       side_effect=_mock_open_if_open_fails)
    @mock.patch.object(ckan.lib.uploader, '_storage_path',
                       new='/doesnt_exist')
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper


class MockFieldStorage(cgi.FieldStorage):

    def __init__(self, fp, filename):

        self.file = fp
        self.filename = filename
        self.name = 'upload'
        self.list = None
