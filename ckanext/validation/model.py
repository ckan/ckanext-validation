# encoding: utf-8

import datetime
import uuid
import logging
import six

from sqlalchemy import Column, Unicode, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import JSON

from ckan.model.meta import metadata

log = logging.getLogger(__name__)


def make_uuid():
    return six.text_type(uuid.uuid4())


Base = declarative_base(metadata=metadata)


class Validation(Base):
    __tablename__ = u'validation'

    id = Column(Unicode, primary_key=True, default=make_uuid)
    resource_id = Column(Unicode)
    status = Column(Unicode, default=u'created')
    created = Column(DateTime, default=datetime.datetime.utcnow)
    finished = Column(DateTime)
    report = Column(JSON)
    error = Column(JSON)


def create_tables():
    Validation.__table__.create()

    log.info(u'Validation database tables created')


def tables_exist():
    return Validation.__table__.exists()
