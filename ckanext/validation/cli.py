# encoding: utf-8

import click

from ckanext.validation import common


def get_commands():
    return [validation]


@click.group()
def validation():
    """Validation management commands.
    """
    pass


@validation.command(name='init-db')
def init_db():
    """ Initialize database tables.
    """
    common.init_db()


@validation.command(name='run')
@click.option(u'-y', u'--yes',
              help=u'Automatic yes to prompts. Assume "yes" as answer '
                   u'to all prompts and run non-interactively',
              default=False)
@click.option('-r', '--resource',
              multiple=True,
              help=u'Run data validation on a particular resource (if the format is suitable).'
                   u'It can be defined multiple times. Not to be used with -d or -s')
@click.option('-d', '--dataset',
              multiple=True,
              help=u'Run data validation on all resources for a particular dataset (if the format is suitable).'
                   u' You can use the dataset id or name, and it can be defined multiple times. '
                   u'Not to be used with -r or -s')
@click.option('-s', '--search',
              default=False,
              help=u'Extra search parameters that will be used for getting the datasets to run '
                   u'validation on. It must be a JSON object like the one used by the `package_search` API call.'
                   u' Supported fields are `q`, `fq` and `fq_list`. Check the documentation for examples. '
                   u'Note that when using this you will have to specify the resource formats to target yourself.'
                   u' Not to be used with -r or -d.')
def run_validation(yes, resource, dataset, search):
    '''Start asynchronous data validation on the site resources. If no
    options are provided it will run validation on all resources of
    the supported formats (`ckanext.validation.formats`). You can
    specify particular datasets to run the validation on their
    resources. You can also pass arbitrary search parameters to filter
    the selected datasets.
    '''
    common.run_validation(yes, resource, dataset, search)


@validation.command()
@click.option(u'-o', u'--output',
              help=u'Location of the CSV validation report file on the relevant commands.',
              default=u'validation_errors_report.csv')
def report(output):
    '''Generate a report with all current data validation reports. This
    will print an overview of the total number of tabular resources
    and a breakdown of how many have a validation status of success,
    failure or error. Additionally it will create a CSV report with all
    failing resources, including the following fields:
        * Dataset name
        * Resource id
        * Resource URL
        * Status
        * Validation report URL
    '''
    common.report(output)


@validation.command(name='report-full')
@click.option(u'-o', u'--output',
              help=u'Location of the CSV validation report file on the relevant commands.',
              default=u'validation_errors_report.csv')
def report_full(output):
    '''Generate a detailed report. This is similar to 'report'
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
    common.report(output, full=True)
