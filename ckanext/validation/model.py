# encoding: utf-8

import datetime
import uuid
import logging

from sqlalchemy import Column, Unicode, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import JSON
from six import text_type

from ckan.model.meta import metadata

log = logging.getLogger(__name__)


def make_uuid():
    return text_type(uuid.uuid4())


Base = declarative_base(metadata=metadata)


class Validation(Base):
    __tablename__ = u'validation'

    id = Column(Unicode, primary_key=True, default=make_uuid)
    resource_id = Column(Unicode)
    #  status can be one of these values:
    #     created: Job created and put onto queue
    #     running: Job picked up by worker and being processed
    #     success: Validation Successful and report attached
    #     failure: Validation Failed and report attached
    #     error: Validation Job could not create validation report
    status = Column(Unicode, default=u'created')
    # created is when job was added
    created = Column(DateTime, default=datetime.datetime.utcnow)
    # finished is when report was generated, is None when new or restarted
    finished = Column(DateTime)
    # json object of report, can be None
    report = Column(JSON)
    # json object of error, can be None
    error = Column(JSON)


def create_tables():
    Validation.__table__.create()

    log.info(u'Validation database tables created')


def tables_exist():
    return Validation.__table__.exists()
