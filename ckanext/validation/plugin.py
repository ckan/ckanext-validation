# encoding: utf-8

import logging

import ckan.plugins as p
import ckantoolkit as t

from ckanext.validation.logic import resource_validation_run


log = logging.getLogger(__name__)


class ValidationPlugin(p.SingletonPlugin):
    p.implements(p.IConfigurer)

    p.implements(p.IActions)

    # IConfigurer

    def update_config(self, config_):
        t.add_template_directory(config_, u'templates')
        t.add_public_directory(config_, u'public')
        t.add_resource(u'fanstatic', u'validation')

    # IActions

    def get_actions(self):
        return {
            u'resource_validation_run': resource_validation_run
        }
