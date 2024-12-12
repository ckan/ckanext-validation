import json
import io
import datetime

import pytest

import ckantoolkit as t
from ckantoolkit.tests.factories import Sysadmin, Dataset
from ckantoolkit.tests.helpers import (
    call_action
)

from ckanext.validation.tests.helpers import VALID_CSV, INVALID_CSV


def _new_resource_url(dataset_id):

    url = "/dataset/{}/resource/new".format(dataset_id)

    return url


def _edit_resource_url(dataset_id, resource_id):

    url = "/dataset/{}/resource/{}/edit".format(dataset_id, resource_id)

    return url


def _get_resource_new_page_as_sysadmin(app, id):
    user = Sysadmin()
    env = {"REMOTE_USER": user["name"].encode("ascii")}
    response = app.get(
        url="/dataset/new_resource/{}".format(id),
        extra_environ=env,
    )
    return env, response


def _get_resource_update_page_as_sysadmin(app, id, resource_id):
    user = Sysadmin()
    env = {"REMOTE_USER": user["name"].encode("ascii")}
    response = app.get(
        url="/dataset/{}/resource_edit/{}".format(id, resource_id),
        extra_environ=env,
    )
    return env, response


@pytest.mark.usefixtures("clean_db", "validation_setup", "with_plugins")
class TestResourceSchemaForm(object):
    def test_resource_form_includes_json_fields(self, app):
        dataset = Dataset()
        env, response = _get_resource_new_page_as_sysadmin(app, dataset["id"])
        assert '<input type="hidden" id="field-schema" name="schema"' in response.body
        assert '<input id="field-schema-url" type="url" name="schema_url"' in response.body
        assert '<textarea id="field-schema-json" name="schema_json"' in response.body

    def test_resource_form_create(self, app):
        dataset = Dataset()

        value = {"fields": [{"name": "code"}, {"name": "department"}]}
        json_value = json.dumps(value)

        data = {
            "url": "https://example.com/data.csv",
            "schema": json_value,
            "id": "",
            "save": "",
        }

        user = Sysadmin()
        env = {"REMOTE_USER": user["name"].encode("ascii")}
        app.post(
            url=_new_resource_url(dataset['id']),
            extra_environ=env,
            data=data
        )

        dataset = call_action("package_show", id=dataset["id"])

        assert dataset["resources"][0]["schema"] == value

    def test_resource_form_create_json(self, app):
        dataset = Dataset()

        value = {"fields": [{"name": "code"}, {"name": "department"}]}
        json_value = json.dumps(value)

        data = {
            "url": "https://example.com/data.csv",
            "schema_json": json_value,
            "id": "",
            "save": "",
        }

        user = Sysadmin()
        env = {"REMOTE_USER": user["name"].encode("ascii")}
        app.post(
            url=_new_resource_url(dataset['id']),
            extra_environ=env,
            data=data
        )

        dataset = call_action("package_show", id=dataset["id"])

        assert dataset["resources"][0]["schema"] == value

    def test_resource_form_create_upload(self, app):
        dataset = Dataset()

        value = {"fields": [{"name": "code"}, {"name": "department"}]}
        json_value = bytes(json.dumps(value).encode('utf8'))

        data = {
            "url": "https://example.com/data.csv",
            "id": "",
            "save": "",
            "schema_upload": (io.BytesIO(json_value), "schema.json"),
        }

        user = Sysadmin()
        env = {"REMOTE_USER": user["name"].encode("ascii")}

        app.post(
            url=_new_resource_url(dataset['id']),
            extra_environ=env,
            data=data
        )

        dataset = call_action("package_show", id=dataset["id"])

        assert dataset["resources"][0]["schema"] == value

    def test_resource_form_create_url(self, app):
        dataset = Dataset()

        value = "https://example.com/schemas.json"
        data = {
            "url": "https://example.com/data.csv",
            "schema_url": value,
            "id": "",
            "save": "",
        }

        user = Sysadmin()
        env = {"REMOTE_USER": user["name"].encode("ascii")}

        app.post(
            url=_new_resource_url(dataset['id']),
            extra_environ=env,
            data=data
        )

        dataset = call_action("package_show", id=dataset["id"])

        assert dataset["resources"][0]["schema"] == value

    def test_resource_form_update(self, app):
        value = {"fields": [{"name": "code"}, {"name": "department"}]}
        dataset = Dataset(
            resources=[{"url": "https://example.com/data.csv", "schema": value}]
        )

        value = {"fields": [{"name": "code"}, {"name": "department"}, {"name": "date"}]}

        json_value = json.dumps(value)

        data = {
            "url": "https://example.com/data.csv",
            # Clear current value
            "schema_json": "",
            "schema": json_value,
            "id": "",
            "save": "",
        }

        user = Sysadmin()
        env = {"REMOTE_USER": user["name"].encode("ascii")}

        app.post(
            url=_edit_resource_url(dataset['id'], dataset['resources'][0]['id']),
            extra_environ=env,
            data=data
        )

        dataset = call_action("package_show", id=dataset["id"])

        assert dataset["resources"][0]["schema"] == value

    def test_resource_form_update_json(self, app):
        value = {"fields": [{"name": "code"}, {"name": "department"}]}
        dataset = Dataset(
            resources=[{"url": "https://example.com/data.csv", "schema": value}]
        )

        value = {"fields": [{"name": "code"}, {"name": "department"}, {"name": "date"}]}

        json_value = json.dumps(value)
        data = {
            "url": "https://example.com/data.csv",
            "schema_json": json_value,
            "id": "",
            "save": "",
        }

        user = Sysadmin()
        env = {"REMOTE_USER": user["name"].encode("ascii")}

        app.post(
            url=_edit_resource_url(dataset['id'], dataset['resources'][0]['id']),
            extra_environ=env,
            data=data
        )

        dataset = call_action("package_show", id=dataset["id"])

        assert dataset["resources"][0]["schema"] == value

    def test_resource_form_update_url(self, app):
        value = {"fields": [{"name": "code"}, {"name": "department"}]}
        dataset = Dataset(
            resources=[{"url": "https://example.com/data.csv", "schema": value}]
        )

        value = "https://example.com/schema.json"

        data = {
            "url": "https://example.com/data.csv",
            "schema_url": value,
            "id": "",
            "save": "",
        }

        user = Sysadmin()
        env = {"REMOTE_USER": user["name"].encode("ascii")}

        app.post(
            url=_edit_resource_url(dataset['id'], dataset['resources'][0]['id']),
            extra_environ=env,
            data=data
        )

        dataset = call_action("package_show", id=dataset["id"])

        assert dataset["resources"][0]["schema"] == value

    def test_resource_form_update_upload(self, app):
        value = {"fields": [{"name": "code"}, {"name": "department"}]}
        dataset = Dataset(
            resources=[{"url": "https://example.com/data.csv", "schema": value}]
        )

        value = {"fields": [{"name": "code"}, {"name": "department"}, {"name": "date"}]}
        json_value = bytes(json.dumps(value).encode('utf8'))

        data = {
            "url": "https://example.com/data.csv",
            "id": "",
            "save": "",
            "schema_upload": (io.BytesIO(json_value), "schema.json"),
        }

        user = Sysadmin()
        env = {"REMOTE_USER": user["name"].encode("ascii")}
        app.post(
            url=_edit_resource_url(dataset['id'], dataset['resources'][0]['id']),
            extra_environ=env,
            data=data
        )

        dataset = call_action("package_show", id=dataset["id"])

        assert dataset["resources"][0]["schema"] == value


@pytest.mark.usefixtures("clean_db", "validation_setup")
class TestResourceValidationOptionsForm(object):
    def test_resource_form_includes_json_fields(self, app):
        dataset = Dataset()

        env, response = _get_resource_new_page_as_sysadmin(app, dataset["id"])
        assert '<textarea id="field-validation_options" name="validation_options"' in response.body

    def test_resource_form_create(self, app):
        dataset = Dataset()

        value = {
            "delimiter": ";",
            "headers": 2,
            "skip_rows": ["#"],
        }
        json_value = json.dumps(value)
        data = {
            "url": "https://example.com/data.csv",
            "validation_options": json_value,
            "id": "",
            "save": "",
        }

        user = Sysadmin()
        env = {"REMOTE_USER": user["name"].encode("ascii")}

        app.post(
            url=_new_resource_url(dataset['id']),
            extra_environ=env,
            data=data
        )

        dataset = call_action("package_show", id=dataset["id"])

        assert dataset["resources"][0]["validation_options"] == value

    def test_resource_form_update(self, app):
        value = {
            "delimiter": ";",
            "headers": 2,
            "skip_rows": ["#"],
        }

        dataset = Dataset(
            resources=[
                {"url": "https://example.com/data.csv", "validation_options": value}
            ]
        )

        value = {
            "delimiter": ";",
            "headers": 2,
            "skip_rows": ["#"],
            "skip_tests": ["blank-rows"],
        }

        json_value = json.dumps(value)
        data = {
            "url": "https://example.com/data.csv",
            "validation_options": json_value,
            "id": "",
            "save": "",
        }

        user = Sysadmin()
        env = {"REMOTE_USER": user["name"].encode("ascii")}

        app.post(
            url=_edit_resource_url(dataset['id'], dataset['resources'][0]['id']),
            extra_environ=env,
            data=data
        )

        dataset = call_action("package_show", id=dataset["id"])

        assert dataset["resources"][0]["validation_options"] == value


@pytest.mark.usefixtures("clean_db", "validation_setup", "mock_uploads")
@pytest.mark.ckan_config("ckanext.validation.run_on_create_sync", True)
class TestResourceValidationOnCreateForm(object):

    def test_resource_form_create_valid(self, app):

        dataset = Dataset()

        data = {
            "url": "https://example.com/data.csv",
            "id": "",
            "save": "",
            "upload": (io.BytesIO(bytes(VALID_CSV.encode("utf8"))), "valid.csv"),
        }

        user = Sysadmin()
        env = {"REMOTE_USER": user["name"].encode("ascii")}

        app.post(
            url=_new_resource_url(dataset['id']),
            extra_environ=env,
            data=data
        )

        dataset = call_action("package_show", id=dataset["id"])

        assert dataset["resources"][0]["validation_status"] == "success"
        assert "validation_timestamp" in dataset["resources"][0]

    def test_resource_form_create_invalid(self, app):
        dataset = Dataset()

        data = {
            "url": "https://example.com/data.csv",
            "id": "",
            "save": "",
            "upload": (io.BytesIO(bytes(INVALID_CSV.encode("utf8"))), "invalid.csv"),
        }

        user = Sysadmin()
        env = {"REMOTE_USER": user["name"].encode("ascii")}

        response = app.post(
            url=_new_resource_url(dataset['id']),
            extra_environ=env,
            data=data
        )

        assert "validation" in response.body
        assert "missing-cell" in response.body
        assert 'Row at position \\&#34;2\\&#34; has a missing cell in field \\&#34;d\\&#34; at position \\&#34;4\\&#34;' in response.body
        assert "This row has less values compared to the header row" in response.body


@pytest.mark.usefixtures("clean_db", "validation_setup", "mock_uploads")
@pytest.mark.ckan_config("ckanext.validation.run_on_update_sync", True)
class TestResourceValidationOnUpdateForm(object):

    def test_resource_form_update_valid(self, app):

        dataset = Dataset(resources=[{"url": "https://example.com/data.csv"}])
        data = {
            "url": "https://example.com/data.csv",
            "id": "",
            "save": "",
            "upload": (io.BytesIO(bytes(VALID_CSV.encode("utf8"))), "valid.csv"),
        }

        user = Sysadmin()
        env = {"REMOTE_USER": user["name"].encode("ascii")}

        app.post(
            url=_edit_resource_url(dataset['id'], dataset['resources'][0]['id']),
            extra_environ=env,
            data=data
        )
        dataset = call_action("package_show", id=dataset["id"])

        assert dataset["resources"][0]["validation_status"] == "success"
        assert "validation_timestamp" in dataset["resources"][0]

    def test_resource_form_update_invalid(self, app):

        dataset = Dataset(resources=[{"url": "https://example.com/data.csv"}])

        data = {
            "url": "https://example.com/data.csv",
            "id": "",
            "save": "",
            "upload": (io.BytesIO(bytes(INVALID_CSV.encode("utf8"))), "invalid.csv"),
        }

        user = Sysadmin()
        env = {"REMOTE_USER": user["name"].encode("ascii")}

        call_action("package_show", id=dataset["id"])
        response = app.post(
            url=_edit_resource_url(dataset['id'], dataset['resources'][0]['id']),
            extra_environ=env,
            data=data
        )

        assert "validation" in response.body
        assert "missing-cell" in response.body
        assert "This row has less values compared to the header row" in response.body


@pytest.mark.usefixtures("clean_db", "validation_setup")
class TestResourceValidationFieldsPersisted(object):
    @classmethod
    def setup_class(cls):
        # Needed to apply the config changes at the right time so they can be picked up
        # during startup
        cls._original_config = dict(t.config)
        t.config["ckanext.validation.run_on_update_sync"] = False

    @classmethod
    def teardown_class(cls):

        t.config.clear()
        t.config.update(cls._original_config)

    def test_resource_form_fields_are_persisted(self, app):

        dataset = Dataset(
            resources=[
                {
                    "url": "https://example.com/data.csv",
                    "validation_status": "success",
                    "validation_timestamp": datetime.datetime.now().isoformat(),
                }
            ]
        )

        env, response = _get_resource_update_page_as_sysadmin(
            app, dataset["id"], dataset["resources"][0]["id"]
        )

        assert '<input type="hidden" name="validation_status" value="success"' in response.body
        assert '<input type="hidden" name="validation_timestamp"' in response.body
