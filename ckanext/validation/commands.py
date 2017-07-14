# encoding: utf-8

import sys

import click

from ckan.lib.cli import (
    load_config,
    paster_click_group,
    click_config_option,
)

from ckanext.validation.model import create_tables, tables_exist


validation_group = paster_click_group(
    summary=u'Validate data yo')


@validation_group.command(
    u'init-db',
    help=u'Initialize database tables')
@click.help_option(u'-h', u'--help')
@click_config_option
def init_db(config):
    load_config(config)

    if tables_exist():
        print(u'Validation tables already exist')
        sys.exit(1)

    create_tables()

    print(u'Validation tables created')
