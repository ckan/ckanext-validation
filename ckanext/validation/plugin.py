# encoding: utf-8

import json
import logging
import os

import ckan.plugins as p
import ckan.plugins.toolkit as tk

from ckan.lib.plugins import DefaultTranslation
from .redis_helper import RedisHelper

from . import settings as s, cli, utils, validators, views
from .helpers import get_helpers
from .logic import action, auth

log = logging.getLogger(__name__)


class ValidationPlugin(p.SingletonPlugin, DefaultTranslation):
    p.implements(p.IConfigurer)
    p.implements(p.IActions)
    p.implements(p.IAuthFunctions)
    p.implements(p.IResourceController, inherit=True)
    p.implements(p.IPackageController, inherit=True)
    p.implements(p.ITemplateHelpers)
    p.implements(p.IValidators)
    p.implements(p.ITranslation, inherit=True)
    p.implements(p.IClick)
    p.implements(p.IBlueprint)

    redis = RedisHelper()

    # IClick

    def get_commands(self):
        return cli.get_commands()

    # IBlueprint

    def get_blueprint(self):
        return views.get_blueprints()

    # ITranslation
    def i18n_directory(self):
        u'''Change the directory of the .mo translation files'''
        return os.path.join(
            os.path.dirname(__file__),
            'i18n'
        )

    # IConfigurer

    def update_config(self, config_):
        tk.add_template_directory(config_, u'templates')
        tk.add_resource(u'webassets', 'ckanext-validation')

    # IActions

    def get_actions(self):
        return action.get_actions()

    # IAuthFunctions

    def get_auth_functions(self):
        return auth.get_auth_functions()

    # ITemplateHelpers

    def get_helpers(self):
        return get_helpers()

    # IValidators

    def get_validators(self):
        return validators.get_validators()

    # IResourceController

    def before_resource_create(self, context, data_dict):
        log.debug("before_resource_create - context: %s, data_dict: %s", context, data_dict)
        # Don't run the after_dataset_update validation hook
        # when we're only changing a single resource.
        self.redis.put(data_dict['package_id'], True, 600)

        data_dict = utils.process_schema_fields(data_dict)

        if s.get_create_mode(context, data_dict) == s.ASYNC_MODE:
            log.debug("Skipping before_resource_create validation as we are in async mode")
            return

        if utils.is_resource_could_be_validated(context, data_dict):
            utils.validate_resource(context, data_dict, new_resource=True)
        else:
            log.debug("New resource does not qualify for validation: %s", data_dict)

    def _data_dict_is_dataset(self, data_dict):
        return (
            u'creator_user_id' in data_dict
            or u'owner_org' in data_dict
            or u'resources' in data_dict
            or data_dict.get(u'type') == u'dataset')

    def after_resource_create(self, context, data_dict):
        log.debug("after_resource_create - context: %s, data_dict: %s", context, data_dict)
        if data_dict.pop('_success_validation', False):
            return utils.create_success_validation_job(data_dict["id"])

        if s.get_create_mode(context, data_dict) == s.SYNC_MODE:
            log.debug("Skipping post-create validation when in sync mode")
            return

        if utils.is_resource_could_be_validated(context, data_dict):
            utils.validate_resource(context, data_dict, new_resource=True)
        else:
            log.debug("New resource does not qualify for validation: %s", data_dict)

    def before_resource_update(self, context, current_resource, updated_resource):
        log.debug("before_resource_update - context: %s, data_dict: %s", context, updated_resource)

        # Don't run the after_dataset_update validation hook
        # when we're only changing a single resource.
        self.redis.put(updated_resource['package_id'], True, 600)

        # Avoid loop - skip validation when the current update is
        # the validation job recording its results.
        if self.redis.get(updated_resource['id']):
            log.debug("%s validation is locked, skipping before_resource_update hook", updated_resource['id'])
            return

        updated_resource = utils.process_schema_fields(updated_resource)
        validation_required = utils.is_resource_requires_validation(
            context, current_resource, updated_resource)

        if not validation_required:
            log.debug("Updated resource does not qualify for validation: %s", updated_resource)
            updated_resource['_do_not_validate'] = True
            return

        # if in sync mode, it's better to run it before updating, because
        # the new uploaded file will be here
        if s.get_update_mode(context, updated_resource) == s.SYNC_MODE:
            utils.validate_resource(context, updated_resource)
        else:
            # if it's an async mode, gather ID's and use it in `after_update`
            # because only here we are able to compare current data with new
            self.redis.put(updated_resource['id'] + '/validate', True, 600)

    def after_resource_update(self, context, data_dict):
        log.debug("after_resource_update - context: %s, data_dict: %s", context, data_dict)
        # Finished updating resource, unlock the after_dataset_update hook.
        self.redis.delete(data_dict['package_id'])

        # Avoid loop - skip validation if the current update is
        # the validation job recording its results.
        if self.redis.pop(data_dict['id']) \
                or data_dict.pop(u'_do_not_validate', False) \
                or data_dict.pop('_success_validation', False):
            log.debug("%s validation is locked, skipping after_resource_update hook", data_dict['id'])
            return

        validation_possible = utils.is_resource_could_be_validated(
            context, data_dict)

        if not validation_possible:
            log.info("Resource validation is not possible, ending hook")
            return

        if not self.redis.pop(data_dict['id'] + '/validate'):
            log.warning("Resource ID not marked for validation, ending hook")
            return

        utils.validate_resource(context, data_dict)

    # IPackageController

    def after_dataset_create(self, context, data_dict):
        log.debug("after_dataset_create - context: %s, data_dict: %s", context, data_dict)
        for resource in data_dict.get(u'resources', []):
            if utils.is_resource_could_be_validated(context, resource):
                utils.validate_resource(context, resource, new_resource=True)

    def after_dataset_update(self, context, data_dict):
        log.debug("after_dataset_update - context: %s, data_dict: %s", context, data_dict)
        # Skip package validation if it's already handled.
        if self.redis.pop(data_dict['id']):
            log.debug("%s validation is locked, skipping after_dataset_update hook", data_dict['id'])
            return

        for resource in data_dict.get('resources', []):
            if resource.pop(u'_do_not_validate', False) \
                    or resource.pop('_success_validation', False):
                continue

            if not utils.is_resource_could_be_validated(context, resource):
                log.debug("Updated resource does not qualify for validation: %s", resource)
                continue

            utils.validate_resource(context, resource)

    def before_dataset_index(self, index_dict):
        res_status = []
        dataset_dict = json.loads(index_dict['validated_data_dict'])
        for resource in dataset_dict.get('resources', []):
            if resource.get('validation_status'):
                res_status.append(resource['validation_status'])

        if res_status:
            index_dict['vocab_validation_status'] = res_status

        return index_dict
