# encoding: utf-8

import logging

import ckan.plugins as p
import ckantoolkit as t

from ckanext.validation import settings
from ckanext.validation.model import tables_exist
from ckanext.validation.logic import (
    resource_validation_run, resource_validation_show,
    resource_validation_delete,
    auth_resource_validation_run, auth_resource_validation_show,
    auth_resource_validation_delete,
    resource_create as custom_resource_create,
    # resource_update as custom_resource_update,
)
from ckanext.validation.helpers import (
    get_validation_badge,
    validation_extract_report_from_errors,
    dump_json_value,
)
from ckanext.validation.validators import (
    resource_schema_validator,
)
from ckanext.validation.utils import (
    get_create_mode_from_config,
    get_update_mode_from_config,
)


log = logging.getLogger(__name__)


class ValidationPlugin(p.SingletonPlugin):
    p.implements(p.IConfigurer)
    p.implements(p.IActions)
    p.implements(p.IRoutes, inherit=True)
    p.implements(p.IAuthFunctions)
    p.implements(p.IResourceController, inherit=True)
    p.implements(p.ITemplateHelpers)
    p.implements(p.IValidators)

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
        t.add_resource(u'fanstatic', 'ckanext-validation')

    # IRoutes

    def before_map(self, map_):

        controller = u'ckanext.validation.controller:ValidationController'

        map_.connect(
            u'validation_read',
            u'/dataset/{id}/resource/{resource_id}/validation',
            controller=controller, action=u'validation')

        return map_

    # IActions

    def get_actions(self):
        new_actions = {
            u'resource_validation_run': resource_validation_run,
            u'resource_validation_show': resource_validation_show,
            u'resource_validation_delete': resource_validation_delete,
        }

        if get_create_mode_from_config() == u'sync':
            new_actions[u'resource_create'] = custom_resource_create
        # if get_update_mode_from_config() == u'async':
        #    new_actions[u'resource_update'] = custom_resource_update

        return new_actions

    # IAuthFunctions

    def get_auth_functions(self):
        return {
            u'resource_validation_run': auth_resource_validation_run,
            u'resource_validation_show': auth_resource_validation_show,
            u'resource_validation_delete': auth_resource_validation_delete,
        }

    # ITemplateHelpers

    def get_helpers(self):
        return {
            'get_validation_badge': get_validation_badge,
            'validation_extract_report_from_errors': validation_extract_report_from_errors,
            'dump_json_value': dump_json_value,
        }

    # IResourceController

    resources_to_validate = {}

    def after_create(self, context, resource):

        if not get_create_mode_from_config() == u'async':
            return

        needs_validation = False
        if ((
            # File uploaded
            resource.get(u'url_type') == u'upload' or
            # URL defined
            resource.get(u'url')
            ) and (
            # Make sure format is supported
            resource.get(u'format', u'').lower() in
                settings.SUPPORTED_FORMATS
                )):
            needs_validation = True

        if needs_validation:
            _run_async_validation(resource['id'])

    def before_update(self, context, current_resource, updated_resource):

        if not get_update_mode_from_config() == u'async':
            return

        needs_validation = False
        if ((
            # New file uploaded
            updated_resource.get(u'upload') or
            # External URL changed
            updated_resource.get(u'url') != current_resource.get(u'url') or
            # Schema changed
            (updated_resource.get(u'schema') !=
             current_resource.get(u'schema')) or
            # Format changed
            (updated_resource.get(u'format', u'').lower() !=
             current_resource.get(u'format', u'').lower())
            ) and (
            # Make sure format is supported
            updated_resource.get(u'format', u'').lower() in
                settings.SUPPORTED_FORMATS
                )):
            needs_validation = True

        if needs_validation:
            self.resources_to_validate[updated_resource[u'id']] = True

    def after_update(self, context, updated_resource):

        if not get_update_mode_from_config() == u'async':
            return

        resource_id = updated_resource[u'id']

        if resource_id in self.resources_to_validate:
            del self.resources_to_validate[resource_id]

            _run_async_validation(resource_id)

    # IValidators
    def get_validators(self):
        return {
            'resource_schema_validator': resource_schema_validator,
        }


def _run_async_validation(resource_id):

    try:
        t.get_action(u'resource_validation_run')(
            {u'ignore_auth': True},
            {u'resource_id': resource_id,
             u'async': True})
    except t.ValidationError as e:
        log.warning(
            u'Could not run validation for resource {}: {}'.format(
                resource_id, str(e)))
