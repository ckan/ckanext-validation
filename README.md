# ckanext-validation

[![Build Status](https://travis-ci.org/frictionlessdata/ckanext-validation.svg?branch=master)](https://travis-ci.org/frictionlessdata/ckanext-validation)
[![Coverage Status](https://coveralls.io/repos/github/frictionlessdata/ckanext-validation/badge.svg?branch=master)](https://coveralls.io/github/frictionlessdata/ckanext-validation?branch=master)

Data description and validation for CKAN with [Frictionless Data](https://frictionlessdata.io) tools.


## Table of Contents

  * [Overview](#overview)
  * [Versions supported and requirements](#versions-supported-and-requirements)
  * [Installation](#installation)
  * [Configuration](#configuration)
  * [How it works](#how-it-works)
     * [Data Validation](#data-validation)
     * [Data Schema](#data-schema)
     * [Validation Options](#validation-options)
     * [Operation modes](#operation-modes)
        * [Asynchronous validation](#asynchronous-validation)
        * [Synchronous validation](#synchronous-validation)
     * [Changes in the schema](#changes-in-the-schema)
  * [Action functions](#action-functions)
	* [resource_validation_run](#resource_validation_run)
	* [resource_validation_show](#resource_validation_show)
	* [resource_validation_delete](#resource_validation_delete)
  * [Command Line Interface](#command-line-interface)
    * [Starting the validation process manually](#starting-the-validation-process-manually)
    * [Data validation reports](#data-validation-reports)
  * [Running the Tests](#running-the-tests)
  * [Copying and License](#copying-and-license)


## Overview

This extension brings data validation powered by the [goodtables](https://github.com/frictionlessdata/goodtables-py) library to CKAN. It provides out of the box features to validate tabular data and integrate validation reports to the CKAN interface.

Data validation can be performed automatically on the background or during dataset creation, and the results are stored against each resource.

!['Status badges in resources'](https://i.imgur.com/9VIzfwo.png)

Comprehensive reports are created describing issues found with the data, both at the structure level (missing headers, blank rows, etc) and at the data schema level (wrong data types, values out of range etc).


The extension also exposes all the underlying [actions](#action-functions) so data validation can be integrated in custom workflows from other extensions.

If you are eager to get started, jump to the [Installation](#installation) and [Configuration](#configuration) instructions. To learn more about data validation and how the extension works, read the next section.

## Versions supported and requirements

This extension has been tested with CKAN 2.4 to 2.7.

It is strongly recommended to use it alongside [ckanext-scheming](https://github.com/ckan/ckanext-scheming) to define the necessary extra fields in the default CKAN schema.

If you want to use [asynchronous validation](#asynchronous-validation) with background jobs and are using CKAN 2.6 or lower, [ckanext-rq](https://github.com/ckan/ckanext-rq) is also needed. Please refer to both READMEs for installation instructions.


## Installation

To install ckanext-validation, activate your CKAN virtualenv and run:

    git clone https://github.com/frictionlessdata/ckanext-validation.git
    cd ckanext-validation
    pip install -r requirements.txt
    python setup.py develop

Create the database tables running:

    paster validation init-db -c ../path/to/ini/file


## Configuration

Once installed, add the `validation` plugin to the `ckan.plugins` configuration option on your INI file:

    ckan.plugins = ... validation

*Note:* if using CKAN 2.6 or lower and the [asynchronous validation](#asynchronous-validation) also add the `rq` plugin ([see Versions supported and requirements](#versions-supported-and-requirements)) to `ckan.plugins`.


The extension requires changes in the [CKAN schema](#changes-in-the-schema). The easisest way to add those is by using ckanext-scheming. Use these two configuration options to link to the dataset schema (replace with your own if you need to customize it) and the required presets:

	scheming.dataset_schemas = ckanext.validation.examples:ckan_default_schema.json
	scheming.presets = ckanext.scheming:presets.json
    	               ckanext.validation:presets.json

Use the following configuration options to choose the [operation modes](#operation-modes):

	ckanext.validation.run_on_create_async = True|False (Defaults to True)	
	ckanext.validation.run_on_update_async = True|False (Defaults to True)	

	ckanext.validation.run_on_create_sync = True|False (Defaults to False)	
	ckanext.validation.run_on_update_sync = True|False (Defaults to False)	

By default validation will be run agaisnt the following formats: `CSV`, `XLSX` and `XLS`. You can modify these formats using the following option:

	ckanext.validation.formats = csv xlsx

You can also provide [validation options](#validation-options) that will be used by default when running the validation:

	ckanext.validation.default_validation_options={
	    "skip_checks": ["blank-rows", "duplicate-headers"],
    	"headers": 3}

Make sure to use indentation if the value spans multiple lines otherwise it won't be parsed.


## How it works

### Data Validation

CKAN users will be familiar with the validation performed against the metadata fields when creating or updating datasets. The form will return an error for instance if a field is missing or it doesn't have the expected format.

Data validation follows the same principle but against the actual data published in CKAN, that is the contents of tabular files (Excel, CSV, etc) hosted in CKAN itself or elsewhere. Whenever a resource of the appropiate format is created or updated, the extension will validate the data against a collection of checks. This validation is powered by [goodtables](https://github.com/frictionlessdata/goodtables-py), a very powerful data validation library developed by [Open Knowledge International](https://okfn.org) as part of the [Frictionless Data](https://frictionlessdata.io) project. Goodtables provides an extensive suite of [checks](https://github.com/frictionlessdata/goodtables-py#checks) that cover common issues with tabular data files.

These checks include structural problems like missing headers or values, blank rows, etc., but also can validate the data contents themselves (see [Data Schemas](#data-schemas)) or even run [custom checks](https://github.com/frictionlessdata/goodtables-py#custom-constraint).

The result of this validation is a JSON report. This report contains all the issues found (if any) with their relevant context (row number, columns involved, etc). The reports are stored in the database and linked to the CKAN resource, and can be retrieved [via the API](#resource-validation-show).

If there is a report available for a particular resource, a status badge will be displayed in the resource listing and on the resource page, showing whether validation passed or failed for the resource.

![Status badge](https://i.imgur.com/9LIHMF8.png)

Clicking on the badge will take you to the validation report page, where the report will be rendered.

!['Validation report'](https://i.imgur.com/Mm6vKFD.png)

Whenever possible, the report will provide a preview of the cells, rows or columns involved in an error, to make easy to identify and fix it.

### Data Schema

As we mentioned before, data can be validated against a schema. Much in the same way that the standard CKAN schema for metadata fields, the schema describes the data and what its values are expected to be.

These schemas are defined following the [Table Schema](http://frictionlessdata.io/specs/table-schema/) specification, a really simple and flexible standard for describing tabular data.

Let's see an example. Consider the following table (that could be stored as a CSV or Excel file):

| id  | location | date       | measurement | observations   |
| --- | -------- | ---------- | ----------- | -------------- |
| 1   | 'A'      | 01/02/2017 | 23.65       |                |
| 2   | 'B'      | 21/03/2017 | 22.90       |                |
| 3   | 'A'      | 15/06/2017 | 21.79       | Severe drought |
| 4   | 'C'      | 10/10/2017 | 24.12       |                |
| 5   | 'C'      | 31/10/2017 | 24.21       |                |


The following schema describes the expected data:

```json
{
    "primaryKey": "id",
    "fields": [
        {
            "name": "id",
            "title": "Measurement identifier",
            "type": "integer"
        },
        {
            "name": "location",
            "title": "Measurement location code",
            "type": "string",
            "constraints": {
                "enum": ["A", "B", "C", "D"]
            }
        },
        {
            "name": "date",
            "title": "Measurement date",
            "type": "date",
            "format": "%d/%m/%Y"
        },
        {
            "name": "measurement",
            "title": "Measure of the oblique fractal impedance at noon",
            "type": "number",
            "constraints": {
                "required": true
            }
        },
        {
            "name": "observations",
            "title": "Extra observations",
            "type": "string"
        }
    ]
}

```

If we store this schema agaisnt a resource, it will be used to perform a more thorough validation. For instance, updating the resource with the following data would fail validation with a variety of errors, even if the general structure of the file is correct:


| id  | location | date       | measurement | observations   |
| --- | -------- | ---------- | ----------- | -------------- |
| ... | ...      | ...        | ...         | ...            |
| 5   | 'E'      | 2017-11-01 | missing     |                |
| 'a' | 'B'      | 21/03/2017 |             |                |

With the extension enabled and configured, schemas can be attached to the `schema` field on resources via the UI form or the API. If present in a resource, they will be used when performing validation on the resource file.


### Validation Options

As we saw before, the validation process involves many different checks and it's very likely that what "valid" data actually means will vary across CKAN instances or datasets. The validation process can be tweaked by passing any of the [supported options](https://github.com/frictionlessdata/goodtables-py#validatesource-options) on goodtables. These can be used to add or remove specific checks, control limits, etc.

For instance, the following file would fail validation using the default options, but it may be valid in a given context, or the issues may be known to the publishers:

```
<blank line>
<blank line>
id;group;measurement
# 2017
1;A;23
2;B;24
# 2016
3;C;23
4;C;25
<blank line>
```

The following validation options would make validation pass:

```json
{
    "headers": 3,
    "delimiter": ";",
    "skip_rows": ["#"],
    "skip_checks": ["blank-rows"]
}

```

Validation options can be defined (as a JSON object like the above) on each resource (via the UI form or the API on the `validation_options` field) or can be set globally by administrators on the CKAN INI file (see [Configuration](#configuration)).


### Operation modes

The data validation process described above can be run in two modes: asynchronously in the background or synchronously while the resource is being created or updated. You can choose the mode for each of the create and update actions, but in most cases you will probably need just one of the two modes for both actions.

#### Asynchronous validation

Asynchronous validation is run in the background whenever a resource of a supported format is created or updated. Validation won't affect the action performed, so if there are validation errors found the reource will be created or updated anyway.

This mode might be useful for instances where datasets are harvested from other sources, or where multiple publishers create datasets and as a maintainer you only want to give visibility to the quality of data, encouraging publishers to fix any issues.

You will need to run the `worker` commmand to pick up validation jobs. Please refer to the [background jobs documentation](http://docs.ckan.org/en/latest/maintaining/background-tasks.html) for more details:

    paster jobs worker -c /path/to/ini/file

Use `ckanext.validation.run_on_create_async` and `ckanext.validation.run_on_update_async` to enable this mode (See [Configuration](#configuration)).


#### Synchronous validation

Synchronous validation is performed at the same time a resource of the supported formats is being created or updated. Currently, if data validation errors are found, a `ValidationError` will be raised and you won't be able to create or update the resource.

Validation at creation or update time can be useful to ensure that data quality is maintained or that published data conforms to a particular schema.

When using the UI form, validation errors will be displayed as normal CKAN validation errors:

![Error message](https://i.imgur.com/M9ARlAk.png)

Clicking the link on the error message will bring up a modal window with the validation report rendered:

![Modal window with report](https://i.imgur.com/hx7WSqX.png)

Use `ckanext.validation.run_on_create_sync` and `ckanext.validation.run_on_update_sync` to enable this mode (See [Configuration](#configuration)).


### Changes in the schema

The extension requires changes in the default CKAN resource schema to add some fields it requires. It is strongly recommended to use [ckanext-scheming](https://github.com/ckan/ckanext-scheming) to define your CKAN schema. This extension provides all the necessary presets and validators to get up and running just by adding the following fields to the `resource_fields` section of a ckanext-scheming schema:

```json
    {
      "field_name": "schema",
      "label": "Schema",
      "preset": "resource_schema"
    },
    {
      "field_name": "validation_options",
      "label": "Validation options",
      "preset": "validation_options"
    },
    {
      "field_name": "validation_status",
      "label": "Validation status",
      "preset": "hidden_in_form"
    },
    {
      "field_name": "validation_timestamp",
      "label": "Validation timestamp",
      "preset": "hidden_in_form"
    }

```


Here's more detail on the fields added:

* `schema`: This can be a [Table Schema](http://frictionlessdata.io/specs/table-schema/) JSON object or an URL pointing to one. In the UI form you can upload a JSON file, link to one providing a URL or enter it directly. If uploaded, the file contents will be read and stored in the `schema` field. In all three cases the contents will be validated against the Table Schema specification.
* `validation_options`: A JSON object with validation options that will be passed to [goodtables](https://github.com/frictionlessdata/goodtables-py#validatesource-options).

![Form fields](https://i.imgur.com/ixKOCij.png)

Additionally, two read-only fields are added to resources:

* `validation_status`: Stores the last validation result for the resource. Can be one of `success`, `failure` or `error`.
* `validation_timestamp`: Date and time of the last validation run.


## Action functions

The `validation` plugin adds new API actions to create and display validation reports.
By default `resource_validation_run`, `resource_validation_delete` and `resource_validation_show` inherit whatever auth is in place
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

#### `resource_validation_delete`

```python

def resource_validation_delete(context, data_dict):
    u'''
    Remove the validation job result for a particular resource.
    It also deletes the underlying Validation object.

    :param resource_id: id of the resource to remove validation from
    :type resource_id: string

    :rtype: None

    '''

```

## Command Line Interface

### Starting the validation process manually

You can start (asynchronous) validation jobs from the command line using the `paster validation run` command. If no parameters are provided it will start a validation job for all resources in the site of suitable format (ie `ckanext.validation.formats`):

    paster validation run -c /path/to/ckan/ini

You can limit the resources by specifying a dataset id or name:

    paster validation run -c /path/to/ckan/ini -d statistical-data-2018

Or providing arbitrary search parameters:

    paster validation run -c ../ckan/development.ini -s '{"fq":"res_format:XLSX"}'


### Data validation reports

The extension provides two small utilities to generate a global report with all the current data validation reports:

	paster validation report -c /path/to/ckan/ini

	paster validation report-full -c /path/to/ckan/ini


Both commands will print an overview of the total number of datasets and tabular resources, and a breakdown of how many have a validation status of success,
failure or error. Additionally they will create a CSV report. `paster validation report` will create a report with all failing resources, including the following fields:

* Dataset name
* Resource id
* Resource format
* Resource URL
* Status
* Validation report URL

`paster validation report-full` will add a row on the output CSV for each error found on the validation report (limited to ten occurrences of the same error type per file). So the fields in the generated CSV report will be:

* Dataset name
* Resource id
* Resource format
* Resource URL
* Status
* Error code
* Error message

In both cases you can define the location of the output CSV passing the `-o` or `--output` option:


	paster validation report-full -c /path/to/ckan/ini -o /tmp/reports/validation_full.csv


Check the command help for more details:

	paster validation --help

	Usage: paster validation [options] Utilities for the CKAN data validation extension

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



	Options:
	  -h, --help            show this help message and exit
	  -v, --verbose
	  -c CONFIG, --config=CONFIG
							Config file to use.
	  -f FILE_PATH, --file=FILE_PATH
							File to dump results to (if needed)
	  -y, --yes             Automatic yes to prompts. Assume "yes" as answer to
							all prompts and run non-interactively
	  -r RESOURCE_ID, --resource=RESOURCE_ID
							 Run data validation on a particular resource (if the
							format is suitable). It can be defined multiple times.
							Not to be used with -d or -s
	  -d DATASET_ID, --dataset=DATASET_ID
							 Run data validation on all resources for a particular
							dataset (if the format is suitable). You can use the
							dataset id or name, and it can be defined multiple
							times. Not to be used with -r or -s
	  -s SEARCH_PARAMS, --search=SEARCH_PARAMS
							Extra search parameters that will be used for getting
							the datasets to run validation on. It must be a JSON
							object like the one used by the `package_search` API
							call. Supported fields are `q`, `fq` and `fq_list`.
							Check the documentation for examples. Note that when
							using this you will have to specify the resource
							formats to target yourself. Not to be used with -r or
							-d.
	  -o OUTPUT_FILE, --output=OUTPUT_FILE
							Location of the CSV validation report file on the
							relevant commands.


## Running the Tests

To run the tests, do:

    nosetests --nologcapture --with-pylons=test.ini


## Copying and License

This material is copyright (c) [Open Knowledge International](https://okfn.org).

It is open and licensed under the GNU Affero General Public License (AGPL) v3.0 whose full text may be found at:

http://www.fsf.org/licensing/licenses/agpl-3.0.html
