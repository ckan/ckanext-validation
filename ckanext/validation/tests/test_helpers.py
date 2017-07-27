import datetime

from nose.tools import assert_equals

from ckan.tests.helpers import reset_db, _get_test_app
from ckan.tests import factories

from ckantoolkit import config

from ckanext.validation.helpers import get_validation_badge
from ckanext.validation.model import create_tables, tables_exist


class TestHelpers(object):

    @classmethod
    def setup_class(cls):
        cls._original_config = dict(config)
        config['ckanext.validation.run_on_create'] = False

        reset_db()
        if not tables_exist():
            create_tables()

        app = _get_test_app()
        cls.request_context = app.flask_app.test_request_context()
        cls.request_context.push()


    @classmethod
    def teardown_class(cls):

        cls.request_context.pop()

        config.clear()
        config.update(cls._original_config)

        reset_db()

    def test_get_validation_badge_no_validation(self):

        resource = factories.Resource(
            format='CSV',
        )

        assert_equals(get_validation_badge(resource), '')

    def test_get_validation_badge_success(self):

        resource = factories.Resource(
            format='CSV',
            validation_status='success',
            validation_timestamp=datetime.datetime.utcnow()
        )

        out = get_validation_badge(resource)

        assert 'href="/dataset/{}/resource/{}/validation"'.format(
            resource['package_id'], resource['id']) in out
        assert 'src="/images/badges/data-success-flat.svg"' in out
        assert 'alt="Valid data"' in out
        assert 'title="{}"'.format(resource['validation_timestamp']) in out

    def test_get_validation_badge_failure(self):

        resource = factories.Resource(
            format='CSV',
            validation_status='failure',
            validation_timestamp=datetime.datetime.utcnow()
        )

        out = get_validation_badge(resource)

        assert 'href="/dataset/{}/resource/{}/validation"'.format(
            resource['package_id'], resource['id']) in out
        assert 'src="/images/badges/data-failure-flat.svg"' in out
        assert 'alt="Invalid data"' in out
        assert 'title="{}"'.format(resource['validation_timestamp']) in out

    def test_get_validation_badge_error(self):

        resource = factories.Resource(
            format='CSV',
            validation_status='error',
            validation_timestamp=datetime.datetime.utcnow()
        )

        out = get_validation_badge(resource)

        assert 'href="/dataset/{}/resource/{}/validation"'.format(
            resource['package_id'], resource['id']) in out
        assert 'src="/images/badges/data-error-flat.svg"' in out
        assert 'alt="Error during validation"' in out
        assert 'title="{}"'.format(resource['validation_timestamp']) in out

    def test_get_validation_badge_other(self):

        resource = factories.Resource(
            format='CSV',
            validation_status='not-sure',
        )

        out = get_validation_badge(resource)

        assert 'href="/dataset/{}/resource/{}/validation"'.format(
            resource['package_id'], resource['id']) in out
        assert 'src="/images/badges/data-unknown-flat.svg"' in out
        assert 'alt="Data validation unknown"' in out
        assert 'title=""' in out
