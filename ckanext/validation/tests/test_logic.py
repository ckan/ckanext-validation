from nose.tools import assert_raises
import mock

from ckan.tests.helpers import call_action, reset_db
from ckan.tests import factories

import ckantoolkit as t


class TestAction(object):

    def setup(self):
        reset_db()

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
