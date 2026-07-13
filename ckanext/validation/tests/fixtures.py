import pytest

from ckan.lib import uploader
from ckanext.validation.model import create_tables, tables_exist


@pytest.fixture
def validation_setup():
    if not tables_exist():
        create_tables()


@pytest.fixture
def mock_uploads(ckan_config, monkeypatch, tmp_path):
    monkeypatch.setitem(ckan_config, "ckan.storage_path", str(tmp_path))
    # CKAN >= 2.10 has no module-level _storage_path cache; the config
    # item above is what its uploader reads
    monkeypatch.setattr(uploader, "_storage_path", str(tmp_path),
                        raising=False)
