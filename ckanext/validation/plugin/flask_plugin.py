# -*- coding: utf-8 -*-

from ckan import plugins as p

from ckanext.validation import blueprints, cli


class ValidationMixin(p.SingletonPlugin):
    p.implements(p.IBlueprint)
    p.implements(p.IClick)

    # IBlueprint

    def get_blueprint(self):
        return [blueprints.validation]

    # IClick

    def get_commands(self):
        return [cli.validation]
