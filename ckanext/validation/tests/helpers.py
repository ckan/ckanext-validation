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
