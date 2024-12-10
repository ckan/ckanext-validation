# encoding: utf-8

import csv
import logging
import six
import sys

from ckantoolkit import (c, NotAuthorized,
                         ObjectNotFound, abort, _,
                         render, get_action, config)

from ckanext.validation import settings
from ckanext.validation.logic.action import _search_datasets
from ckanext.validation.model import create_tables, tables_exist


log = logging.getLogger(__name__)

###############################################################################
#                                  Controller                                 #
###############################################################################


def validation(resource_id, id=None):
    try:
        validation = get_action(u'resource_validation_show')(
            {u'user': c.user},
            {u'resource_id': resource_id})

        resource = get_action(u'resource_show')(
            {u'user': c.user},
            {u'id': resource_id})

        package_id = resource[u'package_id']
        if id and id != package_id:
            raise ObjectNotFound("Resource {} not found in package {}".format(resource_id, id))

        dataset = get_action(u'package_show')(
            {u'user': c.user},
            {u'id': id or resource[u'package_id']})

        # Needed for core resource templates
        c.package = c.pkg_dict = dataset
        c.resource = resource

        return render(u'validation/validation_read.html', extra_vars={
            u'validation': validation,
            u'resource': resource,
            u'pkg_dict': dataset,
            u'dataset': dataset,
        })

    except NotAuthorized:
        return abort(403, _(u'Unauthorized to read this validation report'))
    except ObjectNotFound:
        return abort(404, _(u'No validation report exists for this resource'))