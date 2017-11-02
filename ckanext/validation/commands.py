# encoding: utf-8

import sys

from ckantoolkit import CkanCommand

from ckanext.validation.model import create_tables, tables_exist


def init_db():

    if tables_exist():
        print(u'Validation tables already exist')
        sys.exit(1)

    create_tables()

    print(u'Validation tables created')


class Validation(CkanCommand):
    u'''Utilities for the CKAN data validation extension

    Usage:
        paster validation init-db
            Initialize database tables

    '''
    summary = __doc__.split('\n')[0]
    usage = __doc__
    max_args = 9
    min_args = 0

    def __init__(self, name):

        super(Validation, self).__init__(name)

    def command(self):
        self._load_config()

        if len(self.args) != 1:
            self.parser.print_usage()
            sys.exit(1)

        cmd = self.args[0]
        if cmd == 'init-db':
            init_db()
