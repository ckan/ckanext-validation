import pytest

from ckan.lib import uploader
from ckanext.validation.model import create_tables, tables_exist

import ckantoolkit as t


@pytest.fixture
def validation_setup():
    if not tables_exist():
        create_tables()


@pytest.fixture
def mock_uploads(ckan_config, monkeypatch, tmp_path):
    monkeypatch.setitem(ckan_config, "ckan.storage_path", str(tmp_path))
    monkeypatch.setattr(uploader, "_storage_path", str(tmp_path))


@pytest.fixture
def change_config_for_create_sync():
    # Needed to apply the config changes at the right time so they can be picked up
    # during startup
    _original_config = dict(t.config)
    t.config["ckanext.validation.run_on_create_sync"] = True
    yield
    t.config.clear()
    t.config.update(_original_config)


@pytest.fixture
def change_config_for_update_sync():
    # Needed to apply the config changes at the right time so they can be picked up
    # during startup
    _original_config = dict(t.config)
    t.config["ckanext.validation.run_on_update_sync"] = True
    yield
    t.config.clear()
    t.config.update(_original_config)
