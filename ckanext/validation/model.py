# encoding: utf-8
import datetime
import logging

from sqlalchemy import Column, Unicode, DateTime
from sqlalchemy.dialects.postgresql import JSON

from ckan import model
from ckan.model import types as _types
from ckan.model.meta import metadata
from ckan.plugins.toolkit import BaseModel as Base

log = logging.getLogger(__name__)


class Validation(Base):
    __tablename__ = u'validation'

    id = Column('id', Unicode, primary_key=True, default=_types.make_uuid)
    resource_id = Column('resource_id', Unicode, nullable=False)
    #  status can be one of these values:
    #     created: Job created and put onto queue
    #     running: Job picked up by worker and being processed
    #     success: Validation Successful and report attached
    #     failure: Validation Failed and report attached
    #     error: Validation Job could not create validation report
    status = Column('status', Unicode, default=u'created', nullable=False)
    # created is when job was added
    created = Column('created', DateTime, default=datetime.datetime.utcnow, nullable=False)
    # finished is when report was generated, is None when new or restarted
    finished = Column('finished', DateTime, nullable=True)
    # json object of report, can be None
    report = Column('report', JSON, nullable=True)
    # json object of error, can be None
    error = Column('error', JSON, nullable=True)


def create_tables():
    metadata.create_all(model.meta.engine)

    log.info(u'Validation database tables created')
