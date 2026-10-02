import datetime

import pytest
import mock

from ckan.tests import factories

import ckanext.validation.helpers as h
from ckanext.validation.tests.helpers import SCHEMA


def _assert_validation_badge_status(resource, status):
    out = h.get_validation_badge(resource)

    assert 'href="/dataset/{}/resource/{}/validation"'.format(
        resource['package_id'], resource['id']) in out
    assert 'class="status {}"'.format(status) in out


@pytest.mark.usefixtures("clean_db", "validation_setup")
@mock.patch('ckanext.validation.utils.is_resource_could_be_validated',
            return_value=False)
class TestBadges(object):
    """Mocking is_resource_could_be_validated to prevent actual validation,
    because we are not testing it here.

    Validation badge is a mark we are showing on a resource page, to show the
    last validation result"""

    def test_get_validation_badge_no_validation(self, mock_is_validatable):
        resource = factories.Resource(format='CSV', )

        assert h.get_validation_badge(resource) == ''

    def test_hide_validation_badge_no_schema(self, mock_is_validatable):
        resource = factories.Resource(
            format='CSV',
            validation_status='success',
            validation_timestamp=datetime.datetime.utcnow().isoformat())

        assert h.get_validation_badge(resource) == ''

    def test_get_validation_badge_success(self, mock_is_validatable):
        resource = factories.Resource(
            format='CSV',
            validation_status='success',
            validation_timestamp=datetime.datetime.utcnow().isoformat(),
            schema=SCHEMA)

        _assert_validation_badge_status(resource, 'success')

    def test_get_validation_badge_failure(self, mock_is_validatable):
        resource = factories.Resource(
            format='CSV',
            validation_status='failure',
            validation_timestamp=datetime.datetime.utcnow().isoformat(),
            schema=SCHEMA)

        _assert_validation_badge_status(resource, 'invalid')

    def test_get_validation_badge_error(self, mock_is_validatable):
        resource = factories.Resource(
            format='CSV',
            validation_status='error',
            validation_timestamp=datetime.datetime.utcnow().isoformat(),
            schema=SCHEMA)

        _assert_validation_badge_status(resource, 'error')

    def test_get_validation_badge_other(self, mock_is_validatable):
        resource = factories.Resource(
            format='CSV',
            validation_status='not-sure',
            schema=SCHEMA,
        )

        _assert_validation_badge_status(resource, 'unknown')


class TestExtractReportFromErrors(object):

    def test_report_extracted(self):

        report = {'tables': [{'source': '/some/path'}], 'error-count': 8}

        errors = {
            'some_field': ['Some error'],
            'validation': [report],
        }

        extracted_report, errors = h.validation_extract_report_from_errors(
            errors)

        assert extracted_report == report
        assert errors['some_field'] == ['Some error']
        assert str(errors['validation'][0]).strip().startswith(
            'There are validation issues with this file')

        assert 'data-module="modal-dialog"' in str(errors['validation'][0])

    def test_report_not_extracted(self):

        errors = {
            'some_field': ['Some error'],
            'some_other_field': ['Some other error']
        }

        report, errors = h.validation_extract_report_from_errors(errors)

        assert report is None
        assert errors['some_field'] == ['Some error']
        assert errors['some_other_field'] == ['Some other error']


class TestIsUrlValid(object):

    def test_valid_url(self):
        urls = [
            "http://example.com",
            "https://example.com",
            "https://example.com/path?test=1&key=2",
        ]

        for url in urls:
            assert h.is_url_valid(url)

    def test_invalid_url(self):
        urls = [
            "example.com",
            "i am not a url",
            "https://example.com]",
        ]

        for url in urls:
            assert not h.is_url_valid(url)
