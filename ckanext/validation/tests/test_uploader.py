import io
from unittest import mock

import pytest
import responses

from ckantoolkit import config
from ckantoolkit.tests.factories import Sysadmin, Dataset, Resource
from ckantoolkit.tests.helpers import call_action
from ckanext.validation.tests.helpers import VALID_CSV, INVALID_CSV


pytestmark = pytest.mark.usefixtures("clean_db", "validation_setup", "mock_uploads")


def _new_resource_upload_url(dataset_id):

    url = "/dataset/{}/resource/file".format(dataset_id)

    return url


def _edit_resource_upload_url(dataset_id, resource_id):

    url = "/dataset/{}/resource/{}/file".format(dataset_id, resource_id)

    return url


def _get_env():
    user = Sysadmin()
    return {"REMOTE_USER": user["name"]}


# Create resources


def test_create_upload_with_schema(app):

    dataset = Dataset()

    data = {
        "upload": (io.BytesIO(bytes(VALID_CSV.encode("utf8"))), "valid.csv"),
    }

    app.post(
        url=_new_resource_upload_url(dataset["id"]), extra_environ=_get_env(), data=data
    )

    dataset = call_action("package_show", id=dataset["id"])

    assert len(dataset["resources"]) == 1
    assert dataset["resources"][0]["format"] == "CSV"
    assert dataset["resources"][0]["url_type"] == "upload"

    assert dataset["resources"][0]["schema"] == {
        "fields": [
            {"name": "a", "type": "integer"},
            {"name": "b", "type": "integer"},
            {"name": "c", "type": "integer"},
            {"name": "d", "type": "integer"},
        ]
    }


def test_create_upload_no_tabular_no_schema(app):

    dataset = Dataset()

    data = {
        "upload": (io.BytesIO(b"test file"), "some.txt"),
    }

    app.post(
        url=_new_resource_upload_url(dataset["id"]), extra_environ=_get_env(), data=data
    )

    dataset = call_action("package_show", id=dataset["id"])

    assert len(dataset["resources"]) == 1
    assert dataset["resources"][0]["format"] == "TXT"
    assert dataset["resources"][0]["url_type"] == "upload"

    assert "schema" not in dataset["resources"][0]


@responses.activate
def test_create_url_with_schema(app):

    url = "https://example.com/valid.csv"

    responses.add(responses.GET, url, body=VALID_CSV)
    responses.add_passthru(config["solr_url"])

    dataset = Dataset()

    data = {"url": url}

    app.post(
        url=_new_resource_upload_url(dataset["id"]), extra_environ=_get_env(), data=data
    )

    dataset = call_action("package_show", id=dataset["id"])

    assert len(dataset["resources"]) == 1
    assert dataset["resources"][0]["format"] == "CSV"
    assert dataset["resources"][0]["url_type"] is None

    assert dataset["resources"][0]["schema"] == {
        "fields": [
            {"name": "a", "type": "integer"},
            {"name": "b", "type": "integer"},
            {"name": "c", "type": "integer"},
            {"name": "d", "type": "integer"},
        ]
    }


@responses.activate
def test_create_url_no_tabular(app):

    url = "https://example.com/some.txt"

    responses.add(responses.GET, url, body="some text")
    responses.add_passthru(config["solr_url"])

    dataset = Dataset()

    data = {"url": url}

    app.post(
        url=_new_resource_upload_url(dataset["id"]), extra_environ=_get_env(), data=data
    )

    dataset = call_action("package_show", id=dataset["id"])

    assert len(dataset["resources"]) == 1
    assert dataset["resources"][0]["format"] == "TXT"
    assert dataset["resources"][0]["url_type"] is None

    assert "schema" not in dataset["resources"][0]


# Update resources


def test_update_upload_with_schema(app):

    resource = Resource()

    data = {
        "upload": (io.BytesIO(bytes(VALID_CSV.encode("utf8"))), "valid.csv"),
    }

    app.post(
        url=_edit_resource_upload_url(resource["package_id"], resource["id"]),
        extra_environ=_get_env(),
        data=data,
    )

    resource = call_action("resource_show", id=resource["id"])

    assert resource["format"] == "CSV"
    assert resource["url_type"] == "upload"

    assert resource["schema"] == {
        "fields": [
            {"name": "a", "type": "integer"},
            {"name": "b", "type": "integer"},
            {"name": "c", "type": "integer"},
            {"name": "d", "type": "integer"},
        ]
    }


def test_update_upload_no_tabular_no_schema(app):

    resource = Resource()

    data = {
        "upload": (io.BytesIO(b"test file"), "some.txt"),
    }

    app.post(
        url=_edit_resource_upload_url(resource["package_id"], resource["id"]),
        extra_environ=_get_env(),
        data=data,
    )

    resource = call_action("resource_show", id=resource["id"])

    assert resource["format"] == "TXT"
    assert resource["url_type"] == "upload"

    assert "schema" not in resource


def test_update_updates_schema(app):

    dataset = Dataset()

    data = {
        "upload": (io.BytesIO(bytes(VALID_CSV.encode("utf8"))), "valid.csv"),
    }

    app.post(
        url=_new_resource_upload_url(dataset["id"]), extra_environ=_get_env(), data=data
    )

    dataset = call_action("package_show", id=dataset["id"])

    assert dataset["resources"][0]["schema"]

    data = {
        "upload": (io.BytesIO(b"e,f\n5,6"), "some.other.csv"),
    }

    app.post(
        url=_edit_resource_upload_url(dataset["id"], dataset["resources"][0]["id"]),
        extra_environ=_get_env(),
        data=data,
    )

    resource = call_action("resource_show", id=dataset["resources"][0]["id"])

    assert resource["schema"] == {
        "fields": [
            {"name": "e", "type": "integer"},
            {"name": "f", "type": "integer"},
        ]
    }


def test_update_removes_schema(app):

    dataset = Dataset()

    data = {
        "upload": (io.BytesIO(bytes(VALID_CSV.encode("utf8"))), "valid.csv"),
    }

    app.post(
        url=_new_resource_upload_url(dataset["id"]), extra_environ=_get_env(), data=data
    )

    dataset = call_action("package_show", id=dataset["id"])

    assert dataset["resources"][0]["schema"]

    data = {
        "upload": (io.BytesIO(b"test file"), "some.txt"),
    }

    app.post(
        url=_edit_resource_upload_url(dataset["id"], dataset["resources"][0]["id"]),
        extra_environ=_get_env(),
        data=data,
    )

    resource = call_action("resource_show", id=dataset["resources"][0]["id"])

    assert "schema" not in resource


def test_update_upload_no_tabular_no_schema(app):

    resource = Resource()

    data = {
        "upload": (io.BytesIO(b"test file"), "some.txt"),
    }

    app.post(
        url=_edit_resource_upload_url(resource["package_id"], resource["id"]),
        extra_environ=_get_env(),
        data=data,
    )

    resource = call_action("resource_show", id=resource["id"])

    assert resource["format"] == "TXT"
    assert resource["url_type"] == "upload"

    assert "schema" not in resource


@responses.activate
def test_update_url_with_schema(app):
    url = "https://example.com/valid.csv"

    responses.add(responses.GET, url, body=VALID_CSV)
    responses.add_passthru(config["solr_url"])

    resource = Resource()

    data = {
        "url": url,
        # CKAN does not refresh the format, see https://github.com/ckan/ckan/issues/7415
        "format": "CSV",
    }

    app.post(
        url=_edit_resource_upload_url(resource["package_id"], resource["id"]),
        extra_environ=_get_env(),
        data=data,
    )

    resource = call_action("resource_show", id=resource["id"])

    assert resource["format"] == "CSV"
    assert resource["url_type"] is None

    assert resource["schema"] == {
        "fields": [
            {"name": "a", "type": "integer"},
            {"name": "b", "type": "integer"},
            {"name": "c", "type": "integer"},
            {"name": "d", "type": "integer"},
        ]
    }


@responses.activate
def test_update_url_no_tabular_no_schema(app):
    url = "https://example.com/some.txt"

    responses.add(responses.GET, url, body="some text")
    responses.add_passthru(config["solr_url"])

    resource = Resource()

    data = {
        "url": url,
        # CKAN does not refresh the format, see https://github.com/ckan/ckan/issues/7415
        "format": "TXT",
    }

    app.post(
        url=_edit_resource_upload_url(resource["package_id"], resource["id"]),
        extra_environ=_get_env(),
        data=data,
    )

    resource = call_action("resource_show", id=resource["id"])

    assert resource["format"] == "TXT"
    assert resource["url_type"] is None

    assert "schema" not in resource


# Jobs

@pytest.mark.ckan_config("ckanext.validation.run_on_create_async", True)
def test_create_upload_does_not_trigger_async_validations(app):

    dataset = Dataset()

    data = {
        "upload": (io.BytesIO(bytes(VALID_CSV.encode("utf8"))), "valid.csv"),
    }
    with mock.patch("ckanext.validation.plugin._run_async_validation") as mock_validate:
        app.post(
            url=_new_resource_upload_url(dataset["id"]), extra_environ=_get_env(), data=data
        )

        assert not mock_validate.called


@pytest.mark.ckan_config("ckanext.validation.run_on_create_sync", True)
def test_create_upload_does_not_trigger_sync_validations(app):

    dataset = Dataset()

    data = {
        "upload": (io.BytesIO(bytes(VALID_CSV.encode("utf8"))), "valid.csv"),
    }

    with mock.patch("ckanext.validation.logic._run_sync_validation") as mock_validate:
        app.post(
            url=_new_resource_upload_url(dataset["id"]), extra_environ=_get_env(), data=data
        )

        assert not mock_validate.called


@pytest.mark.ckan_config("ckanext.validation.run_on_update_async", True)
def test_update_upload_does_not_trigger_async_validations(app):

    resource = Resource()

    data = {
        "upload": (io.BytesIO(bytes(VALID_CSV.encode("utf8"))), "valid.csv"),
        # CKAN does not refresh the format, see https://github.com/ckan/ckan/issues/7415
        "format": "CSV",
    }

    with mock.patch("ckanext.validation.plugin._run_async_validation") as mock_validate:
        app.post(
            url=_edit_resource_upload_url(resource["package_id"], resource["id"]),
            extra_environ=_get_env(),
            data=data,
        )

        assert not mock_validate.called


@pytest.mark.ckan_config("ckanext.validation.run_on_update_sync", True)
def test_update_upload_does_not_trigger_sync_validations(app):

    resource = Resource()

    data = {
        "upload": (io.BytesIO(bytes(VALID_CSV.encode("utf8"))), "valid.csv"),
        # CKAN does not refresh the format, see https://github.com/ckan/ckan/issues/7415
        "format": "CSV",
    }

    with mock.patch("ckanext.validation.logic._run_sync_validation") as mock_validate:
        app.post(
            url=_edit_resource_upload_url(resource["package_id"], resource["id"]),
            extra_environ=_get_env(),
            data=data,
        )

        assert not mock_validate.called
