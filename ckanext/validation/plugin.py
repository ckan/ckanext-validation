# encoding: utf-8

import json
import logging



import ckan.plugins as p
import ckantoolkit as tk

from . import settings as s, utils, validators, utils
from .helpers import get_helpers
from .logic import action, auth
from .model import tables_exist

from ckanext.validation.interfaces import IDataValidation
from ckanext.validation import views, cli


log = logging.getLogger(__name__)


class ValidationPlugin(p.SingletonPlugin):
    p.implements(p.IConfigurer)
    p.implements(p.IActions)
    p.implements(p.IAuthFunctions)
    p.implements(p.IResourceController, inherit=True)
    p.implements(p.IPackageController, inherit=True)
    p.implements(p.ITemplateHelpers)
    p.implements(p.IValidators)
    p.implements(p.IBlueprint)
    p.implements(p.IClick)

    # IBlueprint

    def get_blueprint(self):
        return views.get_blueprints()

    # IClick

    def get_commands(self):
        return cli.get_commands()

    # IConfigurer

    def update_config(self, config_):
        if not tables_exist():
            init_command = 'ckan validation init-db'
            log.critical(u'''
The validation extension requires a database setup.
Validation pages will not be enabled.
Please run the following to create the database tables:
    %s''', init_command)
        else:
            log.debug(u'Validation tables exist')

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

    resources_to_validate = {}
    packages_to_skip = {}


    # CKAN < 2.10
    def before_create(self, context, data_dict):
        return self.before_resource_create(context, data_dict)

    # CKAN >= 2.10
    def before_resource_create(self, context, data_dict):

        is_dataset = self._data_dict_is_dataset(data_dict)
        if not is_dataset:
            context["_resource_create_call"] = True
            return utils.process_schema_fields(data_dict)

    # CKAN < 2.10
    def after_create(self, context, data_dict):
        # if (self._data_dict_is_dataset(data_dict)):
        #     return self.after_dataset_create(context, data_dict)
        # else:
        return self.after_resource_create(context, data_dict)

    # CKAN >= 2.10
    def after_resource_create(self, context, data_dict):

        is_dataset = self._data_dict_is_dataset(data_dict)

        if not s.get_create_mode_from_config() == u'async':
            return

        if is_dataset:
            for resource in data_dict.get(u'resources', []):
                self._handle_validation_for_resource(context, resource)
        else:
            # This is a resource. Resources don't need to be handled here
            # as there is always a previous `package_update` call that will
            # trigger the `before_update` and `after_update` hooks
            pass

    def _data_dict_is_dataset(self, data_dict):
        return (
            u'creator_user_id' in data_dict
            or u'owner_org' in data_dict
            or u'resources' in data_dict
            or data_dict.get(u'type') == u'dataset')

    def _handle_validation_for_resource(self, context, resource):
        needs_validation = False
        if ((
            # File uploaded
            resource.get(u'url_type') == u'upload' or
            # URL defined
            resource.get(u'url')
            ) and (
            # Make sure format is supported
            resource.get(u'format', u'').lower() in
                s.get_supported_formats()
                )):
            needs_validation = True

        if needs_validation:

            for plugin in p.PluginImplementations(IDataValidation):
                if not plugin.can_validate(context, resource):
                    log.debug('Skipping validation for resource %s', resource['id'])
                    return

            utils.run_async_validation(resource[u'id'])

    # CKAN < 2.10
    def before_update(self, context, current_resource, updated_resource):
        return self.before_resource_update(context, current_resource, updated_resource)

    # CKAN >= 2.10
    def before_resource_update(self, context, current_resource, updated_resource):

        updated_resource = utils.process_schema_fields(updated_resource)

        # the call originates from a resource API, so don't validate the entire package
        package_id = updated_resource.get('package_id')
        if not package_id:
            existing_resource = tk.get_action('resource_show')(
                context={'ignore_auth': True}, data_dict={'id': updated_resource['id']})
            if existing_resource:
                package_id = existing_resource['package_id']
        self.packages_to_skip[package_id] = True

        if not s.get_update_mode_from_config() == u'async':
            return updated_resource

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
                s.get_supported_formats()
                )):
            needs_validation = True

        if needs_validation:
            self.resources_to_validate[updated_resource[u'id']] = True

        return updated_resource

    # CKAN < 2.10
    def after_update(self, context, data_dict):
        # if (self._data_dict_is_dataset(data_dict)):
        #     return self.after_dataset_update(context, data_dict)
        # else:
        return self.after_resource_update(context, data_dict)

    # CKAN >= 2.10
    def after_resource_update(self, context, data_dict):

        is_dataset = self._data_dict_is_dataset(data_dict)

        # Need to allow create as well because resource_create calls
        # package_update
        if (not s.get_update_mode_from_config() == u'async'
                and not s.get_create_mode_from_config() == u'async'):
            return

        if context.get('_validation_performed'):
            # Ugly, but needed to avoid circular loops caused by the
            # validation job calling resource_patch (which calls
            # package_update)
            del context['_validation_performed']
            return

        if is_dataset:
            package_id = data_dict.get('id')
            if self.packages_to_skip.pop(package_id, None) or context.get('save', False):
                # Either we're updating an individual resource,
                # or we're updating the package metadata via the web form;
                # in both cases, we don't need to validate every resource.
                return

            if context.pop("_resource_create_call", False):
                new_resource = data_dict["resources"][-1]
                if new_resource:
                    # This is part of a resource_create call, we only need to validate
                    # the new resource being created
                    self._handle_validation_for_resource(context, new_resource)
                    return

            for resource in data_dict.get(u'resources', []):
                if resource[u'id'] in self.resources_to_validate:
                    # This is part of a resource_update call, it will be
                    # handled on the next `after_update` call
                    continue
                else:
                    # This is an actual package_update call, validate the
                    # resources if necessary
                    self._handle_validation_for_resource(context, resource)

        else:
            # This is a resource
            resource_id = data_dict[u'id']

            if resource_id in self.resources_to_validate:
                for plugin in p.PluginImplementations(IDataValidation):
                    if not plugin.can_validate(context, data_dict):
                        log.debug('Skipping validation for resource %s', data_dict['id'])
                        return

                del self.resources_to_validate[resource_id]

                utils.run_async_validation(resource_id)

            if utils.should_remove_unsupported_resource_validation_reports(data_dict):
                p.toolkit.enqueue_job(fn=utils.remove_unsupported_resource_validation_reports, args=[resource_id])

    # IPackageController

    # CKAN < 2.10
    def before_index(self, index_dict):
        if (self._data_dict_is_dataset(index_dict)):
            return self.before_dataset_index(index_dict)

    # CKAN >= 2.10
    def before_dataset_index(self, index_dict):

        res_status = []
        dataset_dict = json.loads(index_dict['validated_data_dict'])
        for resource in dataset_dict.get('resources', []):
            if resource.get('validation_status'):
                res_status.append(resource['validation_status'])

        if res_status:
            index_dict['vocab_validation_status'] = res_status

        return index_dict
