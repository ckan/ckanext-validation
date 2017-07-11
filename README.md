# ckanext-validation

Data description and validation for CKAN with [Frictionless Data](https://frictionlessdata.io) tools.

## Installation

To install ckanext-validation, activate your CKAN virtualenv and run:

    git clone https://github.com//ckanext-validation.git
    cd ckanext-validation
    python setup.py develop

Once installed, add the `validation` plugin to the `ckan.plugins` configuration option on your INI file:

    ckan.plugins = ... validation


## Running the Tests

To run the tests, do:

    nosetests --nologcapture --with-pylons=test.ini
