import os
import uuid
from unittest import mock

from ckantoolkit import config

from ckantoolkit.tests.factories import Resource

import pytest
from pyfakefs import fake_filesystem_unittest

from ckanext.validation.tests.helpers import mock_uploads_fake_fs
from ckanext.validation.utils import (
    get_create_mode_from_config,
    get_update_mode_from_config,
    get_local_upload_path,
    delete_local_uploaded_file,
    turn_off_validation,
)


class TestConfig(object):
    def test_config_defaults(self):

        assert get_update_mode_from_config() == "async"
        assert get_create_mode_from_config() == "async"

    @pytest.mark.ckan_config("ckanext.validation.run_on_update_sync", True)
    def test_config_update_true_sync(self):

        assert get_update_mode_from_config() == "sync"

    @pytest.mark.ckan_config("ckanext.validation.run_on_update_sync", False)
    def test_config_update_false_sync(self):

        assert get_update_mode_from_config() == "async"

    @pytest.mark.ckan_config("ckanext.validation.run_on_create_sync", True)
    def test_config_create_true_sync(self):

        assert get_create_mode_from_config() == "sync"

    @pytest.mark.ckan_config("ckanext.validation.run_on_create_sync", False)
    def test_config_create_false_sync(self):

        assert get_create_mode_from_config() == "async"

    @pytest.mark.ckan_config("ckanext.validation.run_on_update_async", True)
    def test_config_update_true_async(self):

        assert get_update_mode_from_config() == "async"

    @pytest.mark.ckan_config("ckanext.validation.run_on_update_async", False)
    def test_config_update_false_async(self):

        assert get_update_mode_from_config() is None

    @pytest.mark.ckan_config("ckanext.validation.run_on_create_async", True)
    def test_config_create_true_async(self):

        assert get_create_mode_from_config() == "async"

    @pytest.mark.ckan_config("ckanext.validation.run_on_create_async", False)
    def test_config_create_false_async(self):

        assert get_create_mode_from_config() is None

    @pytest.mark.ckan_config("ckanext.validation.run_on_update_async", False)
    @pytest.mark.ckan_config("ckanext.validation.run_on_create_async", False)
    def test_config_both_false(self):

        assert get_update_mode_from_config() is None
        assert get_create_mode_from_config() is None


@pytest.mark.usefixtures("clean_db", "validation_setup", "mock_uploads")
class TestTurnOffValidation(object):

    @pytest.mark.ckan_config("ckanext.validation.run_on_update_async", True)
    @pytest.mark.ckan_config("ckanext.validation.run_on_create_async", True)
    def test_turn_off_async(self):
        assert config["ckanext.validation.run_on_update_async"] is True
        assert config["ckanext.validation.run_on_create_async"] is True

        with turn_off_validation():
            assert config["ckanext.validation.run_on_update_async"] is False
            assert config["ckanext.validation.run_on_create_async"] is False

            with mock.patch("ckanext.validation.plugin._run_async_validation") as mock_validate:

                Resource()

                assert not mock_validate.called

        assert config["ckanext.validation.run_on_update_async"] is True
        assert config["ckanext.validation.run_on_create_async"] is True

    @pytest.mark.ckan_config("ckanext.validation.run_on_update_sync", True)
    @pytest.mark.ckan_config("ckanext.validation.run_on_create_sync", True)
    def test_turn_off_sync(self):
        assert config["ckanext.validation.run_on_update_sync"] is True
        assert config["ckanext.validation.run_on_create_sync"] is True

        with turn_off_validation():
            assert config["ckanext.validation.run_on_update_sync"] is False
            assert config["ckanext.validation.run_on_create_sync"] is False

            with mock.patch("ckanext.validation.logic._run_sync_validation") as mock_validate:

                Resource()

                assert not mock_validate.called

        assert config["ckanext.validation.run_on_update_sync"] is True
        assert config["ckanext.validation.run_on_create_sync"] is True


    @pytest.mark.ckan_config("ckanext.validation.run_on_update_async", False)
    @pytest.mark.ckan_config("ckanext.validation.run_on_create_sync", True)
    @pytest.mark.ckan_config("ckanext.validation.run_on_update_sync", False)
    def test_turn_off_preserves_values(self):
        assert config["ckanext.validation.run_on_update_async"] is False
        assert "ckanext.validation.run_on_create_async" not in config
        assert config["ckanext.validation.run_on_create_sync"] is True
        assert config["ckanext.validation.run_on_update_sync"] is False

        with turn_off_validation():
            assert config["ckanext.validation.run_on_update_async"] is False
            assert config["ckanext.validation.run_on_create_async"] is False
            assert config["ckanext.validation.run_on_update_sync"] is False
            assert config["ckanext.validation.run_on_create_sync"] is False

            with mock.patch("ckanext.validation.logic._run_sync_validation") as mock_validate:

                Resource()

                assert not mock_validate.called

        assert config["ckanext.validation.run_on_update_async"] is False
        assert "ckanext.validation.run_on_create_async" not in config
        assert config["ckanext.validation.run_on_create_sync"] is True
        assert config["ckanext.validation.run_on_update_sync"] is False


class TestFiles(object):
    @mock_uploads_fake_fs
    def test_local_path(self, mock_open):

        resource_id = str(uuid.uuid4())

        assert get_local_upload_path(
            resource_id
        ) == "/doesnt_exist/resources/{}/{}/{}".format(
            resource_id[0:3], resource_id[3:6], resource_id[6:]
        )

    @mock_uploads_fake_fs
    def test_delete_upload_file(self, mock_open):

        resource_id = str(uuid.uuid4())
        path = "/doesnt_exist/resources/{}/{}/{}".format(
            resource_id[0:3], resource_id[3:6], resource_id[6:]
        )

        patcher = fake_filesystem_unittest.Patcher()
        patcher.setUp()
        patcher.fs.CreateFile(path)

        assert os.path.exists(path)

        delete_local_uploaded_file(resource_id)

        assert not os.path.exists(path)

        patcher.tearDown()

    @mock_uploads_fake_fs
    def test_delete_file_not_deleted_if_resources_first(self, mock_open):

        resource_id = str(uuid.uuid4())
        path = "/doesnt_exist/resources/{}".format(resource_id)

        patcher = fake_filesystem_unittest.Patcher()
        patcher.setUp()
        patcher.fs.CreateFile(path)

        assert os.path.exists(path)
        with mock.patch(
            "ckanext.validation.utils.get_local_upload_path", return_value=path
        ):
            delete_local_uploaded_file(resource_id)

        assert not os.path.exists(path)
        assert os.path.exists("/doesnt_exist/resources")

        patcher.tearDown()

    @mock_uploads_fake_fs
    def test_delete_file_not_deleted_if_resources_second(self, mock_open):

        resource_id = str(uuid.uuid4())
        path = "/doesnt_exist/resources/data/{}".format(resource_id)

        patcher = fake_filesystem_unittest.Patcher()
        patcher.setUp()
        patcher.fs.CreateFile(path)

        assert os.path.exists(path)
        with mock.patch(
            "ckanext.validation.utils.get_local_upload_path", return_value=path
        ):
            delete_local_uploaded_file(resource_id)

        assert not os.path.exists(path)
        assert os.path.exists("/doesnt_exist/resources")

        patcher.tearDown()

    @mock_uploads_fake_fs
    def test_delete_passes_if_os_exeception(self, mock_open):

        resource_id = str(uuid.uuid4())
        path = "/doesnt_exist/resources/{}/{}/{}".format(
            resource_id[0:3], resource_id[3:6], resource_id[6:]
        )

        patcher = fake_filesystem_unittest.Patcher()
        patcher.setUp()
        patcher.fs.CreateFile(path)

        assert os.path.exists(path)
        with mock.patch("ckanext.validation.utils.os.remove", side_effect=OSError):

            delete_local_uploaded_file(resource_id)

        patcher.tearDown()
