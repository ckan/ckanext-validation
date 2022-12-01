import datetime
import io
import json

import pytest
from unittest import mock

from ckan import model
from ckan.tests.helpers import call_action, call_auth
from ckan.tests import factories

import ckantoolkit as t

from ckanext.validation.model import Validation
from ckanext.validation.tests.helpers import (
    VALID_CSV,
    INVALID_CSV,
    VALID_REPORT,
    MockFieldStorage,
    get_mock_file,
)


Session = model.Session


@pytest.mark.usefixtures("clean_db", "validation_setup", "with_plugins")
class TestResourceValidationRun(object):
    def test_resource_validation_run_param_missing(self):

        pytest.raises(t.ValidationError, call_action, "resource_validation_run")

    def test_resource_validation_run_not_exists(self):

        pytest.raises(
            t.ObjectNotFound,
            call_action,
            "resource_validation_run",
            resource_id="not_exists",
        )

    def test_resource_validation_wrong_format(self):

        resource = factories.Resource(format="pdf")

        with pytest.raises(t.ValidationError) as e:

            call_action("resource_validation_run", resource_id=resource["id"])

        assert "Unsupported resource format" in str(e)

    def test_resource_validation_no_url_or_upload(self):

        resource = factories.Resource(url="", format="csv")

        with pytest.raises(t.ValidationError) as e:

            call_action("resource_validation_run", resource_id=resource["id"])

        assert "Resource must have a valid URL" in str(e)

    @mock.patch("ckanext.validation.logic.enqueue_job")
    def test_resource_validation_with_url(self, mock_enqueue_job):

        resource = factories.Resource(url="http://example.com", format="csv")

        call_action("resource_validation_run", resource_id=resource["id"])

    @mock.patch("ckanext.validation.logic.enqueue_job")
    def test_resource_validation_with_upload(self, mock_enqueue_job):

        resource = factories.Resource(url="", url_type="upload", format="csv")

        call_action("resource_validation_run", resource_id=resource["id"])

    def test_resource_validation_run_starts_job(self):

        resource = factories.Resource(format="csv")

        jobs = call_action("job_list")

        call_action("resource_validation_run", resource_id=resource["id"])

        jobs_after = call_action("job_list")

        assert len(jobs_after) == len(jobs) + 1

    @mock.patch("ckanext.validation.logic.enqueue_job")
    def test_resource_validation_creates_validation_object(self, mock_enqueue_job):

        resource = factories.Resource(format="csv")

        call_action("resource_validation_run", resource_id=resource["id"])

        validation = (
            Session.query(Validation)
            .filter(Validation.resource_id == resource["id"])
            .one()
        )

        assert validation.resource_id == resource["id"]
        assert validation.status == "created"
        assert validation.created
        assert validation.finished is None
        assert validation.report is None
        assert validation.error is None

    @pytest.mark.ckan_config("ckanext.validation.run_on_create_async", False)
    @mock.patch("ckanext.validation.logic.enqueue_job")
    def test_resource_validation_resets_existing_validation_object(
        self, mock_enqueue_job
    ):

        resource = {"format": "CSV", "url": "https://some.url"}

        dataset = factories.Dataset(resources=[resource])

        timestamp = datetime.datetime.utcnow()
        old_validation = Validation(
            resource_id=dataset["resources"][0]["id"],
            created=timestamp,
            finished=timestamp,
            status="valid",
            report={"some": "report"},
            error={"some": "error"},
        )

        Session.add(old_validation)
        Session.commit()

        call_action(
            "resource_validation_run", resource_id=dataset["resources"][0]["id"]
        )

        validation = (
            Session.query(Validation)
            .filter(Validation.resource_id == dataset["resources"][0]["id"])
            .one()
        )

        assert validation.resource_id == dataset["resources"][0]["id"]
        assert validation.status == "created"
        assert validation.created is not timestamp
        assert validation.finished is None
        assert validation.report is None
        assert validation.error is None

    @mock.patch("ckanext.validation.logic.enqueue_job")
    def test_resource_validation_only_called_on_resource_created(
        self, mock_enqueue_job
    ):

        resource1 = {"format": "CSV", "url": "https://some.url"}

        dataset = factories.Dataset(resources=[resource1])

        assert mock_enqueue_job.call_count == 1
        assert mock_enqueue_job.call_args[0][1][0]["id"] == dataset["resources"][0]["id"]

        mock_enqueue_job.reset_mock()

        resource2 = call_action(
            "resource_create",
            package_id=dataset["id"],
            name="resource_2",
            format="CSV",
            url="https://some.url"
        )

        assert mock_enqueue_job.call_count == 1
        assert mock_enqueue_job.call_args[0][1][0]["id"] == resource2["id"]

    @mock.patch("ckanext.validation.logic.enqueue_job")
    def test_resource_validation_only_called_on_resource_updated(
        self, mock_enqueue_job
    ):

        resource1 = {"name": "resource_1", "format": "CSV", "url": "https://some.url"}
        resource2 = {"name": "resource_2", "format": "CSV", "url": "https://some.url"}

        dataset = factories.Dataset(resources=[resource1, resource2])

        assert mock_enqueue_job.call_count == 2

        mock_enqueue_job.reset_mock()

        resource_1_id = [r["id"] for r in dataset["resources"] if r["name"] == "resource_1"][0]

        call_action(
            "resource_update",
            id=resource_1_id,
            name="resource_1",
            format="CSV",
            url="https://some.updated.url",
            description="updated"
        )

        assert mock_enqueue_job.call_count == 1
        assert mock_enqueue_job.call_args[0][1][0]["id"] == resource_1_id



@pytest.mark.usefixtures("clean_db", "validation_setup", "with_plugins")
class TestResourceValidationShow(object):
    def test_resource_validation_show_param_missing(self):

        pytest.raises(t.ValidationError, call_action, "resource_validation_show")

    def test_resource_validation_show_not_exists(self):

        pytest.raises(
            t.ObjectNotFound,
            call_action,
            "resource_validation_show",
            resource_id="not_exists",
        )

    @pytest.mark.ckan_config("ckanext.validation.run_on_create_async", False)
    def test_resource_validation_show_validation_does_not_exists(self):

        resource = {"format": "CSV", "url": "https://some.url"}

        dataset = factories.Dataset(resources=[resource])

        pytest.raises(
            t.ObjectNotFound,
            call_action,
            "resource_validation_show",
            resource_id=dataset["resources"][0]["id"],
        )

    @pytest.mark.ckan_config("ckanext.validation.run_on_create_async", False)
    def test_resource_validation_show_returns_all_fields(self):

        resource = {"format": "CSV", "url": "https://some.url"}

        dataset = factories.Dataset(resources=[resource])

        timestamp = datetime.datetime.utcnow()
        validation = Validation(
            resource_id=dataset["resources"][0]["id"],
            created=timestamp,
            finished=timestamp,
            status="valid",
            report={"some": "report"},
            error={"some": "error"},
        )
        Session.add(validation)
        Session.commit()

        validation_show = call_action(
            "resource_validation_show", resource_id=dataset["resources"][0]["id"]
        )

        assert validation_show["id"] == validation.id
        assert validation_show["resource_id"] == validation.resource_id
        assert validation_show["status"] == validation.status
        assert validation_show["report"] == validation.report
        assert validation_show["error"] == validation.error
        assert validation_show["created"] == validation.created.isoformat()
        assert validation_show["finished"] == validation.finished.isoformat()


@pytest.mark.usefixtures("clean_db", "validation_setup", "with_plugins")
class TestResourceValidationDelete(object):
    def test_resource_validation_delete_param_missing(self):

        pytest.raises(t.ValidationError, call_action, "resource_validation_delete")

    def test_resource_validation_delete_not_exists(self):

        pytest.raises(
            t.ObjectNotFound,
            call_action,
            "resource_validation_delete",
            resource_id="not_exists",
        )

    @pytest.mark.ckan_config("ckanext.validation.run_on_create_async", False)
    @pytest.mark.ckan_config("ckanext.validation.run_on_update_async", False)
    def test_resource_validation_delete_removes_object(self):

        resource = factories.Resource(format="csv")
        timestamp = datetime.datetime.utcnow()
        validation = Validation(
            resource_id=resource["id"],
            created=timestamp,
            finished=timestamp,
            status="valid",
            report={"some": "report"},
            error={"some": "error"},
        )
        Session.add(validation)
        Session.commit()

        count_before = (
            Session.query(Validation)
            .filter(Validation.resource_id == resource["id"])
            .count()
        )

        assert count_before == 1

        call_action("resource_validation_delete", resource_id=resource["id"])

        count_after = (
            Session.query(Validation)
            .filter(Validation.resource_id == resource["id"])
            .count()
        )

        assert count_after == 0


@pytest.mark.usefixtures("clean_db", "validation_setup", "with_plugins")
class TestAuth(object):
    def test_run_anon(self):

        resource = factories.Resource()

        context = {"user": None, "model": model}

        pytest.raises(
            t.NotAuthorized,
            call_auth,
            "resource_validation_run",
            context=context,
            resource_id=resource["id"],
        )

    def test_run_sysadmin(self):

        resource = factories.Resource()
        sysadmin = factories.Sysadmin()

        context = {"user": sysadmin["name"], "model": model}

        assert (
            call_auth(
                "resource_validation_run", context=context, resource_id=resource["id"]
            )
            is True
        )

    def test_run_non_auth_user(self):

        user = factories.User()
        org = factories.Organization()
        dataset = factories.Dataset(
            owner_org=org["id"], resources=[factories.Resource()]
        )

        context = {"user": user["name"], "model": model}

        pytest.raises(
            t.NotAuthorized,
            call_auth,
            "resource_validation_run",
            context=context,
            resource_id=dataset["resources"][0]["id"],
        )

    def test_run_auth_user(self):

        user = factories.User()
        org = factories.Organization(
            users=[{"name": user["name"], "capacity": "editor"}]
        )
        dataset = factories.Dataset(
            owner_org=org["id"], resources=[factories.Resource()]
        )

        context = {"user": user["name"], "model": model}

        assert (
            call_auth(
                "resource_validation_run",
                context=context,
                resource_id=dataset["resources"][0]["id"],
            )
            is True
        )

    def test_delete_anon(self):

        resource = factories.Resource()

        context = {"user": None, "model": model}

        pytest.raises(
            t.NotAuthorized,
            call_auth,
            "resource_validation_delete",
            context=context,
            resource_id=resource["id"],
        )

    def test_delete_sysadmin(self):

        resource = factories.Resource()
        sysadmin = factories.Sysadmin()

        context = {"user": sysadmin["name"], "model": model}

        assert (
            call_auth(
                "resource_validation_delete",
                context=context,
                resource_id=resource["id"],
            )
            is True
        )

    def test_delete_non_auth_user(self):

        user = factories.User()
        org = factories.Organization()
        dataset = factories.Dataset(
            owner_org=org["id"], resources=[factories.Resource()]
        )

        context = {"user": user["name"], "model": model}

        pytest.raises(
            t.NotAuthorized,
            call_auth,
            "resource_validation_delete",
            context=context,
            resource_id=dataset["resources"][0]["id"],
        )

    def test_delete_auth_user(self):

        user = factories.User()
        org = factories.Organization(
            users=[{"name": user["name"], "capacity": "editor"}]
        )
        dataset = factories.Dataset(
            owner_org=org["id"], resources=[factories.Resource()]
        )

        context = {"user": user["name"], "model": model}

        assert (
            call_auth(
                "resource_validation_delete",
                context=context,
                resource_id=dataset["resources"][0]["id"],
            )
            is True
        )

    def test_show_anon(self):

        resource = factories.Resource()

        context = {"user": None, "model": model}

        assert (
            call_auth(
                "resource_validation_show", context=context, resource_id=resource["id"]
            )
            is True
        )

    def test_show_anon_public_dataset(self):

        user = factories.User()
        org = factories.Organization()
        dataset = factories.Dataset(
            owner_org=org["id"], resources=[factories.Resource()], private=False
        )

        context = {"user": user["name"], "model": model}

        assert (
            call_auth(
                "resource_validation_show",
                context=context,
                resource_id=dataset["resources"][0]["id"],
            )
            is True
        )

    def test_show_anon_private_dataset(self):

        user = factories.User()
        org = factories.Organization()
        dataset = factories.Dataset(
            owner_org=org["id"], resources=[factories.Resource()], private=True
        )

        context = {"user": user["name"], "model": model}

        pytest.raises(
            t.NotAuthorized,
            call_auth,
            "resource_validation_run",
            context=context,
            resource_id=dataset["resources"][0]["id"],
        )


@pytest.mark.usefixtures("clean_db", "validation_setup", "with_plugins")
@pytest.mark.ckan_config("ckanext.validation.run_on_create_sync", True)
class TestResourceValidationOnCreate(object):

    @pytest.mark.usefixtures("mock_uploads")
    def test_validation_fails_on_upload(self):

        invalid_file = get_mock_file(INVALID_CSV)

        mock_upload = MockFieldStorage(invalid_file, "invalid.csv")

        dataset = factories.Dataset()

        with pytest.raises(t.ValidationError) as e:

            call_action(
                "resource_create",
                package_id=dataset["id"],
                format="CSV",
                upload=mock_upload,
            )

        assert "validation" in e.value.error_dict
        assert "missing-cell" in str(e)
        assert 'Row at position "2" has a missing cell in field "d" at position "4"' in str(e)

    @pytest.mark.usefixtures("mock_uploads")
    def test_validation_fails_no_validation_object_stored(self):

        invalid_file = get_mock_file(INVALID_CSV)

        mock_upload = MockFieldStorage(invalid_file, "invalid.csv")

        dataset = factories.Dataset()

        invalid_stream = io.BufferedReader(io.BytesIO(INVALID_CSV.encode('utf8')))

        validation_count_before = model.Session.query(Validation).count()

        with pytest.raises(t.ValidationError):
            call_action(
                "resource_create",
                package_id=dataset["id"],
                format="CSV",
                upload=mock_upload,
            )

        validation_count_after = model.Session.query(Validation).count()

        assert validation_count_after == validation_count_before

    @pytest.mark.usefixtures("mock_uploads")
    def test_validation_passes_on_upload(self):

        valid_file = get_mock_file(VALID_CSV)

        mock_upload = MockFieldStorage(valid_file, "invalid.csv")

        dataset = factories.Dataset()

        valid_stream = io.BufferedReader(io.BytesIO(VALID_CSV.encode('utf8')))

        with mock.patch("io.open", return_value=valid_stream):

            resource = call_action(
                "resource_create",
                package_id=dataset["id"],
                format="CSV",
                upload=mock_upload,
            )

        assert resource["validation_status"] == "success"
        assert "validation_timestamp" in resource

    @mock.patch("ckanext.validation.jobs.validate", return_value=VALID_REPORT)
    def test_validation_passes_with_url(self, mock_validate):

        url = "https://example.com/valid.csv"

        dataset = factories.Dataset()

        resource = call_action(
            "resource_create",
            package_id=dataset["id"],
            format="csv",
            url=url,
        )

        assert resource["validation_status"] == "success"
        assert "validation_timestamp" in resource


@pytest.mark.usefixtures("clean_db", "validation_setup", "with_plugins")
@pytest.mark.ckan_config("ckanext.validation.run_on_update_sync", True)
class TestResourceValidationOnUpdate(object):

    @pytest.mark.usefixtures("mock_uploads")
    def test_validation_fails_on_upload(self):

        dataset = factories.Dataset(resources=[{"url": "https://example.com/data.csv"}])

        invalid_file = get_mock_file(INVALID_CSV)

        mock_upload = MockFieldStorage(invalid_file, "invalid.csv")

        invalid_stream = io.BufferedReader(io.BytesIO(INVALID_CSV.encode('utf8')))

        with mock.patch("io.open", return_value=invalid_stream):

            with pytest.raises(t.ValidationError) as e:

                call_action(
                    "resource_update",
                    id=dataset["resources"][0]["id"],
                    format="CSV",
                    upload=mock_upload,
                )

        assert "validation" in e.value.error_dict
        assert "missing-cell" in str(e)
        assert 'Row at position "2" has a missing cell in field "d" at position "4"' in str(e)

    @pytest.mark.usefixtures("mock_uploads")
    def test_validation_fails_no_validation_object_stored(self):

        dataset = factories.Dataset(resources=[{"url": "https://example.com/data.csv"}])

        invalid_file = get_mock_file(INVALID_CSV)

        mock_upload = MockFieldStorage(invalid_file, "invalid.csv")

        invalid_stream = io.BufferedReader(io.BytesIO(INVALID_CSV.encode('utf8')))

        with mock.patch("io.open", return_value=invalid_stream):

            with pytest.raises(t.ValidationError):

                call_action(
                    "resource_update",
                    id=dataset["resources"][0]["id"],
                    format="CSV",
                    upload=mock_upload,
                )

        validation_count_after = model.Session.query(Validation).count()

        assert validation_count_after == 0

    @pytest.mark.usefixtures("mock_uploads")
    def test_validation_passes_on_upload(self):

        dataset = factories.Dataset(resources=[{"url": "https://example.com/data.csv"}])

        valid_file = get_mock_file(VALID_CSV)

        mock_upload = MockFieldStorage(valid_file, "valid.csv")

        valid_stream = io.BufferedReader(io.BytesIO(VALID_CSV.encode('utf8')))

        with mock.patch("io.open", return_value=valid_stream):

            resource = call_action(
                "resource_update",
                id=dataset["resources"][0]["id"],
                format="CSV",
                upload=mock_upload,
            )

        assert resource["validation_status"] == "success"
        assert "validation_timestamp" in resource

    @mock.patch("ckanext.validation.jobs.validate", return_value=VALID_REPORT)
    def test_validation_passes_with_url(self, mock_validate):

        dataset = factories.Dataset(resources=[{"url": "https://example.com/data.csv"}])

        resource = call_action(
            "resource_update",
            id=dataset["resources"][0]["id"],
            format="CSV",
            url="https://example.com/some.other.csv",
        )

        assert resource["validation_status"] == "success"
        assert "validation_timestamp" in resource


@pytest.mark.usefixtures("clean_db", "validation_setup", "with_plugins")
class TestSchemaFields(object):
    def test_schema_field(self):

        dataset = factories.Dataset()

        resource = call_action(
            "resource_create",
            package_id=dataset["id"],
            url="http://example.com/file.csv",
            schema='{"fields":[{"name":"id"}]}',
        )

        assert resource["schema"] == {"fields": [{"name": "id"}]}

        assert "schema_upload" not in resource
        assert "schema_url" not in resource

    def test_schema_field_url(self):

        url = "https://example.com/schema.json"

        dataset = factories.Dataset()

        resource = call_action(
            "resource_create",
            package_id=dataset["id"],
            url="http://example.com/file.csv",
            schema=url,
        )

        assert resource["schema"] == url

        assert "schema_upload" not in resource
        assert "schema_url" not in resource

    def test_schema_url_field(self):

        url = "https://example.com/schema.json"

        dataset = factories.Dataset()

        resource = call_action(
            "resource_create",
            package_id=dataset["id"],
            url="http://example.com/file.csv",
            schema_url=url,
        )

        assert resource["schema"] == url

        assert "schema_upload" not in resource
        assert "schema_url" not in resource

    def test_schema_url_field_wrong_url(self):

        url = "not-a-url"

        pytest.raises(
            t.ValidationError,
            call_action,
            "resource_create",
            url="http://example.com/file.csv",
            schema_url=url,
        )

    @pytest.mark.usefixtures("mock_uploads")
    def test_schema_upload_field(self):

        schema_file = io.StringIO('{"fields":[{"name":"category"}]}')

        mock_upload = MockFieldStorage(schema_file, "schema.json")

        dataset = factories.Dataset()

        resource = call_action(
            "resource_create",
            package_id=dataset["id"],
            url="http://example.com/file.csv",
            schema_upload=mock_upload,
        )

        assert resource["schema"] == {"fields": [{"name": "category"}]}

        assert "schema_upload" not in resource
        assert "schema_url" not in resource


@pytest.mark.usefixtures("clean_db", "validation_setup", "with_plugins")
class TestValidationOptionsField(object):
    def test_validation_options_field(self):

        dataset = factories.Dataset()

        validation_options = {
            "delimiter": ";",
            "headers": 2,
            "skip_rows": ["#"],
        }

        resource = call_action(
            "resource_create",
            package_id=dataset["id"],
            url="http://example.com/file.csv",
            validation_options=validation_options,
        )

        assert resource["validation_options"] == validation_options

    def test_validation_options_field_string(self):

        dataset = factories.Dataset()

        validation_options = """{
            "delimiter": ";",
            "headers": 2,
            "skip_rows": ["#"]
        }"""

        resource = call_action(
            "resource_create",
            package_id=dataset["id"],
            url="http://example.com/file.csv",
            validation_options=validation_options,
        )

        assert resource["validation_options"] == json.loads(validation_options)
