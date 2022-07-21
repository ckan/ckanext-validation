#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

from flask import Blueprint

import ckan.plugins as plugins
from ckanext.validation.controller import validation
from ckanext.validation.model import create_tables, tables_exist

class MixinPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IBlueprint)
    plugins.implements(plugins.IClick)

    def get_commands(self):
        import click

        @click.group("validation")
        @click.command("init-db")
        def init_db():
            if tables_exist():
                click.echo("Validation tables already exist")
                sys.exit(0)

            create_tables()

            click.echo("Validation tables created")

        return [init_db]

    
    def get_blueprint(self):
        blueprint = Blueprint('validation', __name__)
        blueprint.add_url_rule("/dataset/{id}/resource/{resource_id}/validation", view_func=validation, endpoint='validation_read', methods=['GET'])
        return blueprint
