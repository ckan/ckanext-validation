import json

import pytest
import factory
import responses
import six
from faker import Faker

import ckan.plugins.toolkit as tk
from ckan.lib import uploader
from ckan.tests import factories

from ckanext.validation.model import create_tables
from ckanext.validation.tests.helpers import VALID_CSV, MockFileStorage, SCHEMA


fake = Faker()


@pytest.fixture
def validation_setup(monkeypatch, ckan_config, tmpdir):
    monkeypatch.setitem(ckan_config, u'ckan.storage_path', str(tmpdir))
    monkeypatch.setattr(uploader, u'get_storage_path', lambda: str(tmpdir))

    create_tables()


@pytest.fixture
def org():
    return factories.Organization()


@pytest.fixture
def dataset(org):
    return factories.Dataset(private=True, owner_org=org['id'])


@pytest.fixture
def mocked_responses():
    solr_url = tk.config.get('solr_url', 'http://127.0.0.1:8983/solr/ckan')

    with responses.RequestsMock() as rsps:
        rsps.add_passthru(solr_url)
        yield rsps


class ResourceFactory(factories.Resource):
    id = fake.uuid4()
    description = fake.sentence()
    schema = factory.LazyAttribute(lambda _: json.dumps(SCHEMA))
    format = "CSV"
    url = None
    url_type = "upload"
    upload = factory.LazyAttribute(
        lambda _: MockFileStorage(six.BytesIO(VALID_CSV), 'data.csv'))


@pytest.fixture
def resource_factory():
    return ResourceFactory


@pytest.fixture
def resource():
    return ResourceFactory()
