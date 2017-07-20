# encoding: utf-8

import logging

import ckan.plugins as p
import ckantoolkit as t

from ckanext.validation import settings
from ckanext.validation.model import tables_exist
from ckanext.validation.logic import (
    resource_validation_run, resource_validation_show,
    auth_resource_validation_run, auth_resource_validation_show)


log = logging.getLogger(__name__)


class ValidationPlugin(p.SingletonPlugin):
    p.implements(p.IConfigurer)
    p.implements(p.IActions)
    p.implements(p.IAuthFunctions)
    p.implements(p.IResourceController, inherit=True)

    # IConfigurer

    def update_config(self, config_):
        if not tables_exist():
            log.critical(u'''
The validation extension requires a database setup. Please run the following
to create the database tables:
    paster --plugin=ckanext-validation validation init-db
''')
        else:
            log.debug(u'Validation tables exist')

        t.add_template_directory(config_, u'templates')
        t.add_public_directory(config_, u'public')
        t.add_resource(u'fanstatic', u'validation')

    # IActions

    def get_actions(self):
        return {
            u'resource_validation_run': resource_validation_run,
            u'resource_validation_show': resource_validation_show
        }

    # IAuthFunctions

    def get_auth_functions(self):
        return {
            u'resource_validation_run': auth_resource_validation_run,
            u'resource_validation_show': auth_resource_validation_show
        }

    # IResourceController

    resources_to_validate = {}

    def before_update(self, context, current_resource, updated_resource):

        needs_validation = False
        if ((
            # New file uploaded
            updated_resource.get('upload') or
            # External URL changed
            updated_resource.get('url') != current_resource.get('url') or
            # Schema changed
            updated_resource.get('schema') != current_resource.get('schema') or
            # Format changed
            (updated_resource.get('format').lower() !=
             current_resource.get('format').lower())
            ) and (
            # Make sure format is supported
            updated_resource.get('format').lower() in
                settings.SUPPORTED_FORMATS
                )):
            needs_validation = True

        if needs_validation:
            self.resources_to_validate[updated_resource['id']] = True

    def after_update(self, context, updated_resource):
        resource_id = updated_resource['id']

        if resource_id in self.resources_to_validate:
            del self.resources_to_validate[resource_id]

            try:
                t.get_action('resource_validation_run')(
                    {'ignore_auth': True},
                    {'resource_id': resource_id})
            except t.ValidationError as e:
                log.warning(
                    'Could not run validation for resource {}: {}'.format(
                        resource_id, str(e)))
