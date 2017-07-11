# encoding: utf-8

import click

from ckan.lib.cli import (
    load_config,
    paster_click_group,
    click_config_option,
)
from ckan.plugins import toolkit as t


validation_group = paster_click_group(
    summary=u'Validate data yo')


@validation_group.command(
    u'run',
    help=u'run fam')
@click.help_option(u'-h', u'--help')
@click_config_option
@click.pass_context
def set_permissions(ctx, config):
    load_config(config or ctx.obj['config'])
    t.enqueue_job(run_validation, ['Caracola'])
    print "Hola"


def run_validation(text):
    print text
