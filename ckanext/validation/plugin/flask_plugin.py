# -*- coding: utf-8 -*-

from ckan import plugins as p

from ckanext.validation import blueprints


class ValidationMixin(p.SingletonPlugin):
    p.implements(p.IBlueprint)

    # IBlueprint

    def get_blueprint(self):
        return [blueprints.validation]
