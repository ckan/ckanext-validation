import sys

import click

from ckanext.validation.model import create_tables, tables_exist


@click.group()
def validation():
    """Harvests remotely mastered metadata."""
    pass


@validation.command()
def init_db():
    """Creates the necessary tables in the database."""
    if tables_exist():
        print(u"Validation tables already exist")
        sys.exit(0)

    create_tables()
    print(u"Validation tables created")
