# ckanext-validation

[![Build Status](https://travis-ci.org/frictionlessdata/ckanext-validation.svg?branch=master)](https://travis-ci.org/frictionlessdata/ckanext-validation)
[![Coverage Status](https://coveralls.io/repos/github/frictionlessdata/ckanext-validation/badge.svg?branch=master)](https://coveralls.io/github/frictionlessdata/ckanext-validation?branch=master)

Data description and validation for CKAN with [Frictionless Data](https://frictionlessdata.io) tools.

## Installation

To install ckanext-validation, activate your CKAN virtualenv and run:

    git clone https://github.com//ckanext-validation.git
    cd ckanext-validation
    python setup.py develop

Create the database tables running:
    
    paster validation init-db -c ../route/to/ini/file

Once installed, add the `validation` plugin to the `ckan.plugins` configuration option on your INI file:

    ckan.plugins = ... validation


## Running the Tests

To run the tests, do:

    nosetests --nologcapture --with-pylons=test.ini
