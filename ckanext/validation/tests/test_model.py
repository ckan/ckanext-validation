from unittest import mock

import pytest

from ckan import model as ckan_model

from ckanext.validation import model as validation_model


class TestTablesExist(object):

    def test_no_engine_yet(self):
        # On first load plugin.update_config runs before model.init_model,
        # so there is no engine to inspect; tables_exist() must not crash
        # (`validation init-db` creates the tables later).
        with mock.patch.object(ckan_model.meta, "engine", None):
            assert validation_model.tables_exist() is True

    @pytest.mark.usefixtures("clean_db", "validation_setup")
    def test_tables_exist_after_init(self):
        # SQLAlchemy 1.4 (CKAN >= 2.10) removed Table.exists(); make sure
        # the inspector-based check still sees the created tables.
        assert validation_model.tables_exist() is True
