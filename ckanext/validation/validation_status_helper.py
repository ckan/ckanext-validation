# encoding: utf-8

import datetime
import logging

from ckan.model import Session
from ckanext.validation import model
from sqlalchemy.orm.exc import NoResultFound

log = logging.getLogger(__name__)

REDIS_PREFIX = 'ckanext-validation:'


class StatusTypes:
    # could be Enum but keeping it system for now
    created = u'created'  # Job created and put onto queue
    running = u'running'  # Job picked up by worker and being processed
    success = u'success'  # Validation Successful and report attached
    failure = u'failure'  # Validation Failed and report attached
    error = u'error'  # Validation Job could not create validation report


class ValidationStatusHelper:
    """
    Validation status:
    created: Job created and put onto queue
    running: Job picked up by worker and being processed
    success: Validation Successful and report attached
    failure: Validation Failed and report attached
    error: Validation Job could not create validation report

    This class is to help ensure we don't enqueue validation jobs when a job is enqueued in the last hour
    and to stop worker threads from working on jobs which are pending (in progress).

    Use case:
    * Ensure validation job/report is not reset multiple times.
    * To not re-enqueue if job is in 'created','running' for last hour (can't differentiate on running timestamp)
    * Allow job to be enqueued if in 'created','running' if over 1 hour old.
    * Allow validation job to be re-queued in all other states i.e. ('success', 'failure', 'error')
    """

    def getValidationJob(self, session=None, resource_id=None):
        # type: (object, Session, str) -> model.Validation
        """
        Gets Validation record for resource if exists

        :param self:
        :param resource_id:
        :return Validation: Validation record or None
        """
        log.debug("getValidationJob: %s", resource_id)
        try:
            return session.query(model.Validation).filter(
                model.Validation.resource_id == resource_id).order_by(model.Validation.created.desc()).one()
        except NoResultFound:
            return None

    def deleteValidationJob(self, session=None, validationRecord=None):
        # type: (object, Session, model.Validation) -> None
        session.delete(validationRecord)
        session.commit()
        session.flush()

    def createValidationJob(self, session=None, resource_id=None, validationRecord=None):
        # type: (object, Session, str) -> model.Validation
        '''
        If validation object not exist:
            create record in state created with created timestamp of now

        If in state 'created' or 'running' and created time stamp within last hour:
            raise exception ValidationJobAlreadyEnqueued

        Else: (object exists and is in final state(success, failure, error))
            reset record to clean state with status 'created', created with timestamp now


        :param self:
        :param string resource_id: resource_id of job
        :return Validation record
        :throws ValidationJobAlreadyEnqueued exception

        '''
        log.debug("createValidationJob: %s", resource_id)
        if validationRecord is None:
            validationRecord = self.getValidationJob(session, resource_id)

        if validationRecord is not None:
            status = validationRecord.status
            ##TODO: review if the time delay will affect xloader integration.
            if status in (StatusTypes.running, StatusTypes.created) and self.getHoursSince(validationRecord.created) < 1:
                error_message = "Validation Job already in pending state: {} on resource: {} created on (gmt): {} data: {}"\
                    .format(validationRecord.status, resource_id, validationRecord.created.isoformat(), validationRecord)
                log.error(error_message)
                raise ValidationJobAlreadyEnqueued(error_message)

        if validationRecord is None:
            validationRecord = model.Validation(resource_id=resource_id)

        validationRecord.finished = None
        validationRecord.report = None
        validationRecord.error = None
        validationRecord.created = datetime.datetime.utcnow()
        validationRecord.status = StatusTypes.created

        session.add(validationRecord)
        session.commit()
        session.flush()
        return validationRecord

    def getHoursSince(self, created):
        return (datetime.datetime.utcnow() - created).total_seconds() / (60 * 60)


class ValidationJobAlreadyEnqueued(Exception):
    """A Validation Job is Already Enqueued."""


class ValidationJobDoesNotExist(Exception):
    """A Validation Job does not exist."""


class ValidationJobAlreadyRunning(Exception):
    """A Validation Job is Already Running."""
