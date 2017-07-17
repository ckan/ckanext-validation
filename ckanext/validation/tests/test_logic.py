import datetime

from nose.tools import assert_raises, assert_equals
import mock

from ckan.model import Session
from ckan.tests.helpers import call_action, reset_db
from ckan.tests import factories

from ckanext.validation.model import create_tables, tables_exist, Validation

import ckantoolkit as t


class TestResourceValidationRun(object):

    def setup(self):
        reset_db()
        if not tables_exist():
            create_tables()

    def test_resource_validation_run_param_missing(self):

        assert_raises(
            t.ValidationError,
            call_action, 'resource_validation_run')

    def test_resource_validation_run_not_exists(self):

        assert_raises(
            t.ObjectNotFound,
            call_action, 'resource_validation_run', resource_id='not_exists')

    def test_resource_validation_wrong_format(self):

        resource = factories.Resource(format='pdf')

        with assert_raises(t.ValidationError) as e:

            call_action('resource_validation_run', resource_id=resource['id'])

        assert 'Unsupported resource format' in str(e.exception)

    def test_resource_validation_no_url_or_upload(self):

        resource = factories.Resource(url='', format='csv')

        with assert_raises(t.ValidationError) as e:

            call_action('resource_validation_run', resource_id=resource['id'])

        assert 'Resource must have a valid URL' in str(e.exception)

    @mock.patch('ckantoolkit.enqueue_job')
    def test_resource_validation_with_url(self, mock_enqueue_job):

        resource = factories.Resource(url='http://example.com', format='csv')

        call_action('resource_validation_run', resource_id=resource['id'])

    @mock.patch('ckantoolkit.enqueue_job')
    def test_resource_validation_with_upload(self, mock_enqueue_job):

        resource = factories.Resource(url='', url_type='upload', format='csv')

        call_action('resource_validation_run', resource_id=resource['id'])

    def test_resource_validation_run_starts_job(self):

        resource = factories.Resource(format='csv')

        jobs = call_action('job_list')

        call_action('resource_validation_run', resource_id=resource['id'])

        jobs_after = call_action('job_list')

        assert len(jobs_after) == len(jobs) + 1

    @mock.patch('ckantoolkit.enqueue_job')
    def test_resource_validation_creates_validation_object(
            self, mock_enqueue_job):

        resource = factories.Resource(format='csv')

        call_action('resource_validation_run', resource_id=resource['id'])

        validation = Session.query(Validation).filter(
            Validation.resource_id == resource['id']).one()

        assert_equals(validation.resource_id, resource['id'])
        assert_equals(validation.status, 'created')
        assert validation.created
        assert_equals(validation.finished, None)
        assert_equals(validation.report, None)
        assert_equals(validation.error, None)

    @mock.patch('ckantoolkit.enqueue_job')
    def test_resource_validation_resets_existing_validation_object(
            self, mock_enqueue_job):

        resource = factories.Resource(format='csv')

        timestamp = datetime.datetime.utcnow()
        old_validation = Validation(
            resource_id=resource['id'],
            created=timestamp,
            finished=timestamp,
            status='valid',
            report={'some': 'report'},
            error={'some': 'error'})

        Session.add(old_validation)
        Session.commit()

        call_action('resource_validation_run', resource_id=resource['id'])

        validation = Session.query(Validation).filter(
            Validation.resource_id == resource['id']).one()

        assert_equals(validation.resource_id, resource['id'])
        assert_equals(validation.status, 'created')
        assert validation.created is not timestamp
        assert_equals(validation.finished, None)
        assert_equals(validation.report, None)
        assert_equals(validation.error, None)


class TestResourceValidationShow(object):

    def setup(self):
        reset_db()
        if not tables_exist():
            create_tables()

    def test_resource_validation_show_param_missing(self):

        assert_raises(
            t.ValidationError,
            call_action, 'resource_validation_show')

    def test_resource_validation_show_not_exists(self):

        assert_raises(
            t.ObjectNotFound,
            call_action, 'resource_validation_show', resource_id='not_exists')

    def test_resource_validation_show_validation_does_not_exists(self):

        resource = factories.Resource(format='csv')

        assert_raises(
            t.ObjectNotFound,
            call_action, 'resource_validation_show',
            resource_id=resource['id'])

    def test_resource_validation_show_returns_all_fields(self):

        resource = factories.Resource(format='csv')
        timestamp = datetime.datetime.utcnow()
        validation = Validation(
            resource_id=resource['id'],
            created=timestamp,
            finished=timestamp,
            status='valid',
            report={'some': 'report'},
            error={'some': 'error'})
        Session.add(validation)
        Session.commit()

        validation_show = call_action(
            'resource_validation_show', resource_id=resource['id'])

        assert_equals(validation_show['id'], validation.id)
        assert_equals(validation_show['resource_id'], validation.resource_id)
        assert_equals(validation_show['status'], validation.status)
        assert_equals(validation_show['report'], validation.report)
        assert_equals(validation_show['error'], validation.error)
        assert_equals(
            validation_show['created'], validation.created.isoformat())
        assert_equals(
            validation_show['finished'], validation.finished.isoformat())
