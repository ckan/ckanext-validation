# encoding: utf-8

import sys
import logging
import json

from ckan.lib.cli import query_yes_no
from ckantoolkit import CkanCommand, get_action, ValidationError

from ckanext.validation import settings
from ckanext.validation.model import create_tables, tables_exist


def error(msg):
    '''
    Print an error message to STDOUT and exit with return code 1.
    '''
    sys.stderr.write(msg)
    if not msg.endswith('\n'):
        sys.stderr.write('\n')
    sys.exit(1)


class Validation(CkanCommand):
    u'''Utilities for the CKAN data validation extension

    Usage:
        paster validation init-db
            Initialize database tables

        paster validation run [options]

            Start asynchronous data validation on the site resources. If no
            options are provided it will run validation on all resources of
            the supported formats (`ckanext.validation.formats`). You can
            specify particular datasets to run the validation on their
            resources. You can also pass arbitrary search parameters to filter
            the selected datasets.
    '''
    summary = __doc__.split('\n')[0]
    usage = __doc__
    max_args = 9
    min_args = 0

    def __init__(self, name):

        super(Validation, self).__init__(name)

        self.parser.add_option('-y', '--yes', dest='assume_yes',
                               action='store_true',
                               default=False,
                               help='''Automatic yes to prompts. Assume "yes"
as answer to all prompts and run non-interactively''')

        self.parser.add_option('-d', '--dataset', dest='dataset_id',
                               action='append',
                               help='''
Run data validation on all resources for a particular dataset (if the format
is suitable). You can use the dataset id or name, and it can be defined
multiple times. Not to be used with -d or -s''')

        self.parser.add_option('-s', '--search', dest='search_params',
                               action='store',
                               default=False,
                               help='''Extra search parameters that will be
used for getting the datasets to run validation on. It must be a
JSON object like the one used by the `package_search` API call. Supported
fields are `q`, `fq` and `fq_list`. Check the documentation for examples.
Note that when using this you will have to specify the resource formats to
target yourself. Not to be used with -r or -d.''')

    _page_size = 100

    def command(self):
        self._load_config()

        if len(self.args) != 1:
            self.parser.print_usage()
            sys.exit(1)

        cmd = self.args[0]
        if cmd == 'init-db':
            self.init_db()
        elif cmd == 'run':
            self.run_validation()
        elif cmd == 'clear':
            self.clear()
        else:
            self.parser.print_usage()
            sys.exit(1)

    def init_db(self):

        if tables_exist():
            print(u'Validation tables already exist')
            sys.exit(1)

        create_tables()

        print(u'Validation tables created')

    def run_validation(self):

        log = logging.getLogger(__name__)

        page = 1
        count_resources = 0
        while True:
            query = self._search_datasets(page)

            if page == 1 and query['count'] == 0:
                error('No datasets to create resource views on, exiting...')

            elif page == 1 and not self.options.assume_yes:

                msg = ('\nYou are about to start validation for {0} datasets' +
                       '.\n Do you want to continue?')

                confirm = query_yes_no(msg.format(query['count']))

                if confirm == 'no':
                    error('Command aborted by user')

            if query['results']:
                for dataset in query['results']:

                    if not dataset.get('resources'):
                        continue

                    for resource in dataset['resources']:

                        if (not resource.get(u'format', u'').lower()
                                in settings.SUPPORTED_FORMATS):
                            continue

                        try:
                            get_action(u'resource_validation_run')(
                                {u'ignore_auth': True},
                                {u'resource_id': resource['id'],
                                 u'async': True})

                            msg = ('Resource {} from dataset {} sent to ' +
                                   'the validation queue')
                            log.debug(
                                msg.format(resource['id'], dataset['name']))

                            count_resources += 1

                        except ValidationError as e:
                            log.warning(
                                u'Could not run validation for resource {} ' +
                                u'from dataset {}: {}'.format(
                                    resource['id'], dataset['name'], str(e)))

                if len(query['results']) < self._page_size:
                    break

                page += 1
            else:
                break

        log.info(
            'Done. {} resources sent to the validation queue'.format(
                count_resources))

    def _update_search_params(self, search_data_dict):
        '''
        Update the `package_search` data dict with the user provided parameters

        Supported fields are `q`, `fq` and `fq_list`.

        If the provided JSON object can not be parsed the process stops with
        an error.

        Returns the updated data dict
        '''

        if not self.options.search_params:
            return search_data_dict

        try:
            user_search_params = json.loads(self.options.search_params)
        except ValueError, e:
            error('Unable to parse JSON search parameters: {0}'.format(e))

        if user_search_params.get('q'):
            search_data_dict['q'] = user_search_params['q']

        if user_search_params.get('fq'):
            if search_data_dict['fq']:
                search_data_dict['fq'] += ' ' + user_search_params['fq']
            else:
                search_data_dict['fq'] = user_search_params['fq']

        if (user_search_params.get('fq_list') and
                isinstance(user_search_params['fq_list'], list)):
            search_data_dict['fq_list'].extend(user_search_params['fq_list'])

    def _add_default_formats(self, search_data_dict):

        filter_formats = []

        for _format in settings.DEFAULT_SUPPORTED_FORMATS:
            filter_formats.extend([_format, _format.upper()])

        filter_formats_query = ['+res_format:"{0}"'.format(_format)
                                for _format in filter_formats]
        search_data_dict['fq_list'].append(' OR '.join(filter_formats_query))

    def _search_datasets(self, page=1):
        '''
        Perform a query with `package_search` and return the result

        Results can be paginated using the `page` parameter
        '''

        n = self._page_size

        search_data_dict = {
            'q': '',
            'fq': '',
            'fq_list': [],
            'include_private': True,
            'rows': n,
            'start': n * (page - 1),
        }

        if self.options.dataset_id:

            search_data_dict['q'] = ' OR '.join(
                ['id:{0} OR name:"{0}"'.format(dataset_id)
                 for dataset_id in self.options.dataset_id]
            )

        elif self.options.search_params:

            self._update_search_params(search_data_dict)
        else:
            self._add_default_formats(search_data_dict)

        if not search_data_dict.get('q'):
            search_data_dict['q'] = '*:*'

        query = get_action('package_search')({}, search_data_dict)

        return query
