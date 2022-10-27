import pytest
from unittest import mock
import json
import io

import ckantoolkit

from ckan.lib.uploader import ResourceUpload
from ckan.tests.helpers import call_action
from ckan.tests import factories

from ckanext.validation.model import create_tables, tables_exist, Validation
from ckanext.validation.jobs import run_validation_job, uploader, Session
from ckanext.validation.tests.helpers import (
    VALID_REPORT,
    INVALID_REPORT,
    ERROR_REPORT,
    VALID_REPORT_LOCAL_FILE,
    MockFieldStorage,
    get_mock_file,
)


class MockUploader(ResourceUpload):
    def get_path(self, resource_id):
        return "/tmp/example/{}".format(resource_id)


def mock_get_resource_uploader(data_dict):
    return MockUploader(data_dict)


@pytest.mark.usefixtures("clean_db", "validation_setup")
class TestValidationJob(object):

    @pytest.mark.ckan_config("ckanext.validation.run_on_create_async", False)
    @mock.patch("ckanext.validation.jobs.validate", return_value=VALID_REPORT)
    @mock.patch.object(Session, "commit")
    @mock.patch.object(ckantoolkit, "get_action")
    def test_job_run_no_schema(self, mock_get_action, mock_commit, mock_validate):

        org = factories.Organization()
        dataset = factories.Dataset(private=True, owner_org=org["id"])

        resource = {
            "id": "test",
            "url": "http://example.com/file.csv",
            "format": "csv",
            "package_id": dataset["id"],
        }

        run_validation_job(resource)

        assert mock_validate.call_args[0][0] == "http://example.com/file.csv"
        assert mock_validate.call_args[1]["format"] == "csv"
        assert mock_validate.call_args[1]["schema"] is None

    @mock.patch("ckanext.validation.jobs.validate", return_value=VALID_REPORT)
    @mock.patch.object(Session, "commit")
    @mock.patch.object(ckantoolkit, "get_action")
    def test_job_run_schema(self, mock_get_action, mock_commit, mock_validate):

        org = factories.Organization()
        dataset = factories.Dataset(private=True, owner_org=org["id"])

        schema = {
            "fields": [
                {"name": "id", "type": "integer"},
                {"name": "description", "type": "string"},
            ]
        }
        resource = {
            "id": "test",
            "url": "http://example.com/file.csv",
            "format": "csv",
            "schema": json.dumps(schema),
            "package_id": dataset["id"],
        }

        run_validation_job(resource)

        assert mock_validate.call_args[0][0] == "http://example.com/file.csv"
        assert mock_validate.call_args[1]["format"] == "csv"
        assert mock_validate.call_args[1]["schema"].to_dict() == schema

    @mock.patch("ckanext.validation.jobs.validate", return_value=VALID_REPORT)
    @mock.patch.object(
        uploader, "get_resource_uploader", return_value=mock_get_resource_uploader({})
    )
    @mock.patch.object(Session, "commit")
    @mock.patch.object(ckantoolkit, "get_action")
    def test_job_run_uploaded_file(
        self, mock_get_action, mock_commit, mock_uploader, mock_validate
    ):

        org = factories.Organization()
        dataset = factories.Dataset(private=True, owner_org=org["id"])

        resource = {
            "id": "test",
            "url": "__upload",
            "url_type": "upload",
            "format": "csv",
            "package_id": dataset["id"],
        }

        run_validation_job(resource)

        assert mock_validate.call_args[0][0] == "/tmp/example/{}".format(resource["id"])
        assert mock_validate.call_args[1]["format"] == "csv"
        assert mock_validate.call_args[1]["schema"] is None

    @mock.patch("ckanext.validation.jobs.validate", return_value=VALID_REPORT)
    def test_job_run_valid_stores_validation_object(self, mock_validate):

        resource = factories.Resource(url="http://example.com/file.csv", format="csv")

        run_validation_job(resource)

        validation = (
            Session.query(Validation)
            .filter(Validation.resource_id == resource["id"])
            .one()
        )

        assert validation.status == "success"
        assert json.loads(validation.report) == VALID_REPORT
        assert validation.finished

    @mock.patch("ckanext.validation.jobs.validate", return_value=INVALID_REPORT)
    def test_job_run_invalid_stores_validation_object(self, mock_validate):

        resource = factories.Resource(url="http://example.com/file.csv", format="csv")

        run_validation_job(resource)

        validation = (
            Session.query(Validation)
            .filter(Validation.resource_id == resource["id"])
            .one()
        )

        assert validation.status == "failure"
        assert json.loads(validation.report) == INVALID_REPORT
        assert validation.finished

    @mock.patch("ckanext.validation.jobs.validate", return_value=ERROR_REPORT)
    def test_job_run_error_stores_validation_object(self, mock_validate):

        resource = factories.Resource(url="http://example.com/file.csv", format="csv")

        run_validation_job(resource)

        validation = (
            Session.query(Validation)
            .filter(Validation.resource_id == resource["id"])
            .one()
        )

        assert validation.status == "error"
        assert validation.error == {"message": ['Errors validating the data']}
        assert validation.finished

    @mock.patch(
        "ckanext.validation.jobs.validate", return_value=VALID_REPORT_LOCAL_FILE
    )
    @mock.patch.object(
        uploader, "get_resource_uploader", return_value=mock_get_resource_uploader({})
    )
    def test_job_run_uploaded_file_replaces_paths(self, mock_uploader, mock_validate):

        resource = factories.Resource(url="__upload", url_type="upload", format="csv")

        run_validation_job(resource)

        validation = (
            Session.query(Validation)
            .filter(Validation.resource_id == resource["id"])
            .one()
        )

        report = json.loads(validation.report)
        assert report["tasks"][0]["place"].startswith("http")

    @mock.patch("ckanext.validation.jobs.validate", return_value=VALID_REPORT)
    def test_job_run_valid_stores_status_in_resource(self, mock_validate):

        resource = factories.Resource(url="http://example.com/file.csv", format="csv")

        run_validation_job(resource)

        validation = (
            Session.query(Validation)
            .filter(Validation.resource_id == resource["id"])
            .one()
        )

        updated_resource = call_action("resource_show", id=resource["id"])

        assert updated_resource["validation_status"] == validation.status
        assert (
            updated_resource["validation_timestamp"] == validation.finished.isoformat()
        )

    @pytest.mark.usefixtures("mock_uploads")
    def test_job_local_paths_are_hidden(self):

        invalid_csv = "id,type\n" + "1,a,\n" * 1010
        invalid_file = get_mock_file(invalid_csv)

        mock_upload = MockFieldStorage(invalid_file, "invalid.csv")

        resource = factories.Resource(format="csv", upload=mock_upload)

        invalid_stream = io.BufferedReader(io.BytesIO(invalid_csv.encode('utf8')))

        with mock.patch("io.open", return_value=invalid_stream):
            run_validation_job(resource)

        validation = (
            Session.query(Validation)
            .filter(Validation.resource_id == resource["id"])
            .one()
        )

        report = json.loads(validation.report)
        source = report["tasks"][0]["place"]
        assert source.startswith("http")
        assert source.endswith("invalid.csv")

    @pytest.mark.usefixtures("mock_uploads")
    def test_job_pass_validation_options_string(self):

        invalid_csv = """

a;b;c
#comment
1;2;3
"""

        validation_options = """
         {
            "dialect":  {
              "header": true,
              "headerRows": [2],
              "commentChar": "#",
              "csv": {
                "delimiter": ";"
              }
            }
        }
        """

        invalid_file = get_mock_file(invalid_csv)
        mock_upload = MockFieldStorage(invalid_file, "invalid.csv")

        resource = factories.Resource(
            format="csv", upload=mock_upload, validation_options=validation_options
        )

        invalid_stream = io.BufferedReader(io.BytesIO(invalid_csv.encode('utf8')))

        with mock.patch("io.open", return_value=invalid_stream):

            run_validation_job(resource)

        validation = (
            Session.query(Validation)
            .filter(Validation.resource_id == resource["id"])
            .one()
        )

        report = json.loads(validation.report)
        assert report["valid"] is True
