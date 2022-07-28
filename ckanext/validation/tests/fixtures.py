import pytest

from ckanext.validation.model import create_tables, tables_exist


@pytest.fixture
def validation_setup():
    if not tables_exist():
        create_tables()
