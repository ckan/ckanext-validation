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
