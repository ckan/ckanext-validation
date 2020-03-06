import os
import uuid
import mock

from pyfakefs import fake_filesystem_unittest
from nose.tools import assert_equals

from ckan.tests.helpers import change_config

from ckanext.validation.tests.helpers import mock_uploads
from ckanext.validation.utils import (
    get_create_mode_from_config, get_update_mode_from_config,
    get_local_upload_path, delete_local_uploaded_file
)


class TestConfig(object):

    def test_config_defaults(self):

        assert_equals(get_update_mode_from_config(), 'async')
        assert_equals(get_create_mode_from_config(), 'async')

    @change_config('ckanext.validation.run_on_update_sync', True)
    def test_config_update_true_sync(self):

        assert_equals(get_update_mode_from_config(), 'sync')

    @change_config('ckanext.validation.run_on_update_sync', False)
    def test_config_update_false_sync(self):

        assert_equals(get_update_mode_from_config(), 'async')

    @change_config('ckanext.validation.run_on_create_sync', True)
    def test_config_create_true_sync(self):

        assert_equals(get_create_mode_from_config(), 'sync')

    @change_config('ckanext.validation.run_on_create_sync', False)
    def test_config_create_false_sync(self):

        assert_equals(get_create_mode_from_config(), 'async')

    @change_config('ckanext.validation.run_on_update_async', True)
    def test_config_update_true_async(self):

        assert_equals(get_update_mode_from_config(), 'async')

    @change_config('ckanext.validation.run_on_update_async', False)
    def test_config_update_false_async(self):

        assert_equals(get_update_mode_from_config(), None)

    @change_config('ckanext.validation.run_on_create_async', True)
    def test_config_create_true_async(self):

        assert_equals(get_create_mode_from_config(), 'async')

    @change_config('ckanext.validation.run_on_create_async', False)
    def test_config_create_false_async(self):

        assert_equals(get_create_mode_from_config(), None)

    @change_config('ckanext.validation.run_on_update_async', False)
    @change_config('ckanext.validation.run_on_create_async', False)
    def test_config_both_false(self):

        assert_equals(get_update_mode_from_config(), None)
        assert_equals(get_create_mode_from_config(), None)


class TestFiles(object):

    @mock_uploads
    def test_local_path(self, mock_open):

        resource_id = str(uuid.uuid4())

        assert_equals(
            get_local_upload_path(resource_id),
            '/doesnt_exist/resources/{}/{}/{}'.format(
                resource_id[0:3], resource_id[3:6], resource_id[6:])
        )

    @mock_uploads
    def test_delete_upload_file(self, mock_open):

        resource_id = str(uuid.uuid4())
        path = '/doesnt_exist/resources/{}/{}/{}'.format(
            resource_id[0:3], resource_id[3:6], resource_id[6:]
        )

        patcher = fake_filesystem_unittest.Patcher()
        patcher.setUp()
        patcher.fs.CreateFile(path)

        assert os.path.exists(path)

        delete_local_uploaded_file(resource_id)

        assert not os.path.exists(path)

        patcher.tearDown()

    @mock_uploads
    def test_delete_file_not_deleted_if_resources_first(self, mock_open):

        resource_id = str(uuid.uuid4())
        path = '/doesnt_exist/resources/{}'.format(resource_id)

        patcher = fake_filesystem_unittest.Patcher()
        patcher.setUp()
        patcher.fs.CreateFile(path)

        assert os.path.exists(path)
        with mock.patch('ckanext.validation.utils.get_local_upload_path',
                        return_value=path):
            delete_local_uploaded_file(resource_id)

        assert not os.path.exists(path)
        assert os.path.exists('/doesnt_exist/resources')

        patcher.tearDown()

    @mock_uploads
    def test_delete_file_not_deleted_if_resources_second(self, mock_open):

        resource_id = str(uuid.uuid4())
        path = '/doesnt_exist/resources/data/{}'.format(resource_id)

        patcher = fake_filesystem_unittest.Patcher()
        patcher.setUp()
        patcher.fs.CreateFile(path)

        assert os.path.exists(path)
        with mock.patch('ckanext.validation.utils.get_local_upload_path',
                        return_value=path):
            delete_local_uploaded_file(resource_id)

        assert not os.path.exists(path)
        assert os.path.exists('/doesnt_exist/resources')

        patcher.tearDown()

    @mock_uploads
    def test_delete_passes_if_os_exeception(self, mock_open):

        resource_id = str(uuid.uuid4())
        path = '/doesnt_exist/resources/{}/{}/{}'.format(
            resource_id[0:3], resource_id[3:6], resource_id[6:]
        )

        patcher = fake_filesystem_unittest.Patcher()
        patcher.setUp()
        patcher.fs.CreateFile(path)

        assert os.path.exists(path)
        with mock.patch('ckanext.validation.utils.os.remove',
                        side_effect=OSError):

            delete_local_uploaded_file(resource_id)

        patcher.tearDown()
