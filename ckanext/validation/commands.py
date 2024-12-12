# encoding: utf-8

import sys

from ckantoolkit import CkanCommand

from ckanext.validation import common


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

         paster validation report [options]

            Generate a report with all current data validation reports. This
            will print an overview of the total number of tabular resources
            and a breakdown of how many have a validation status of success,
            failure or error. Additionally it will create a CSV report with all
            failing resources, including the following fields:
                * Dataset name
                * Resource id
                * Resource URL
                * Status
                * Validation report URL

          paster validation report-full [options]

            Generate a detailed report. This is similar to the previous command
            but on the CSV report it will add a row for each error found on the
            validation report (limited to ten occurrences of the same error
            type per file). So the fields in the generated CSV report will be:

                * Dataset name
                * Resource id
                * Resource URL
                * Status
                * Error code
                * Error message


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

        self.parser.add_option('-r', '--resource', dest='resource_id',
                               action='append',
                               help='''
Run data validation on a particular resource (if the format is suitable).
It can be defined multiple times. Not to be used with -d or -s''')

        self.parser.add_option('-d', '--dataset', dest='dataset_id',
                               action='append',
                               help='''
Run data validation on all resources for a particular dataset (if the format
is suitable). You can use the dataset id or name, and it can be defined
multiple times. Not to be used with -r or -s''')

        self.parser.add_option('-s', '--search', dest='search_params',
                               action='store',
                               default=False,
                               help='''Extra search parameters that will be
used for getting the datasets to run validation on. It must be a
JSON object like the one used by the `package_search` API call. Supported
fields are `q`, `fq` and `fq_list`. Check the documentation for examples.
Note that when using this you will have to specify the resource formats to
target yourself. Not to be used with -r or -d.''')

        self.parser.add_option('-o', '--output', dest='output_file',
                               action='store',
                               default='validation_errors_report.csv',
                               help='''Location of the CSV validation
report file on the relevant commands.''')

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
        elif cmd == 'report':
            self.report()
        elif cmd == 'report-full':
            self.report(full=True)
        else:
            self.parser.print_usage()
            sys.exit(1)

    def init_db(self):
        common.init_db()

    def run_validation(self):

        assume_yes = self.options.assume_yes
        resource_ids = self.options.resource_id
        dataset_ids = self.options.dataset_id
        query = self.options.search_params

        common.run_validation(assume_yes, resource_ids, dataset_ids, query)

    def report(self, full=False):

        output_csv = self.options.output_file
        common.report(output_csv, full)
