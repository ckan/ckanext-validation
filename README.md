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

## Configuration options

The following options on your INI file can be used to configure the extension behaviour:

#### `ckanext.validation.run_on_create`

```
ckanext.validation.run_on_create = false
```

Default value: `True`

Perform an automatic validation every time a resource is created (if the format is suitable).


#### `ckanext.validation.run_on_update`

```
ckanext.validation.run_on_update = false
```

Default value: `True`

Perform an automatic validation every time a resource is updated (if the format is suitable).


## Action functions

The `validation` plugin adds two new API actions to create and display validation reports. 
By default `resource_validation_run` and `resource_validation_show` inherit whatever auth is in place
for `resource_update` and `resource_show` respectively.

#### `resource_validation_run`

```python
def resource_validation_run(context, data_dict):
    u'''
    Start a validation job against a resource.
    Returns the identifier for the job started.

    Note that the resource format must be one of the supported ones,
    currently CSV or Excel.

    :param resource_id: id of the resource to validate
    :type resource_id: string

    :rtype: string

    '''
```

#### `resource_validation_show`

```python
def resource_validation_show(context, data_dict):
    u'''
    Display the validation job result for a particular resource.
    Returns a validation object, including the validation report or errors
    and metadata about the validation like the timestamp and current status.

    Validation status can be one of:

    * `created`: The validation job is in the processing queue
    * `running`: Validation is under way
    * `error`: There was an error while performing the validation, eg the file
        could not be downloaded or there was an error reading it
    * `success`: Validation was performed, and no issues were found
    * `failure`: Validation was performed, and there were issues found

    :param resource_id: id of the resource to validate
    :type resource_id: string

    :rtype: dict

    '''
```


## Running the Tests

To run the tests, do:

    nosetests --nologcapture --with-pylons=test.ini
