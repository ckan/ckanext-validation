# encoding: utf-8

from werkzeug.datastructures import FileStorage

MOCK_COULD_BE_VALIDATED = "ckanext.validation.utils.is_resource_could_be_validated"
MOCK_SYNC_VALIDATE = "ckanext.validation.jobs.validate"
MOCK_ASYNC_VALIDATE = "ckanext.validation.jobs.validate"
MOCK_ENQUEUE_JOB = "ckanext.validation.logic.action.tk.enqueue_job"

INVALID_CSV = b'''a,b,c,d
1,2,3
'''
VALID_CSV = b'''a,b,c,d
1,2,foo,4
'''

# Test a string that eventually contains Windows encoding
# but not within the first 10000 characters.
LATIN1_CSV = '''a,b,c,d
1,2,{}CAFÚ VILA FRANCA,4
'''.format('a' * 10000).encode(encoding='iso-8859-1', errors='strict')

SCHEMA = {
    "fields": [{
        "type": "integer",
        "name": "a",
        "format": "default"
    }, {
        "type": "integer",
        "name": "b",
        "format": "default"
    }, {
        "type": "string",
        "name": "c",
        "format": "default"
    }, {
        "type": "integer",
        "name": "d",
        "format": "default"
    }]
}

NEW_SCHEMA = {
    "fields": [{
        "type": "integer",
        "name": "a",
        "format": "default"
    }, {
        "type": "integer",
        "name": "b",
        "format": "default"
    }]
}

# GOODTABLES_VALID_REPORT = {
#     'error-count': 0,
#     'table-count': 1,
#     'tasks': [{
#         'error-count': 0,
#         'errors': [],
#         'headers': ['name', 'ward', 'party', 'other'],
#         'row-count': 79,
#         'place': 'http://example.com/valid.csv',
#         'time': 0.007,
#         'valid': True
#     }],
#     'time': 0.009,
#     'valid': True,
#     'warnings': []
# }
VALID_REPORT = {
    "valid": True,
    "stats": {"tasks": 1, "errors": 0, "warnings": 0, "seconds": 0.004},
    "warnings": [],
    "errors": [],
    "tasks": [{
        "name": "7e-983a-40b0-a19d-6d2882e48bd6",
        "type": "table",
        "valid": True,
        "place": "http://example.com/file.csv",
        "labels": ["a", "b", "c", "d"],
        "stats": {"errors": 0, "warnings": 0, "seconds": 0.004,
                  "md5": "8cade61428f8180df2cf36d529155b73",
                  "sha256": "b8aec688ba37da9b8c3079f96f1ab8cf711ff7ded3ce4751bdb77acb0c182033",
                  "bytes": 25, "fields": 4, "rows": 1},
        "warnings": [],
        "errors": []
    }]
}

# GOODTABLES_INVALID_REPORT = {
#     'error-count': 2,
#     'table-count': 1,
#     'tasks': [{
#         'error-count': 2,
#         'errors': [
#             {
#                 'code': 'blank-header',
#                 'column-number': 3,
#                 'message': 'Header in column 3 is blank',
#                 'row': None,
#                 'row-number': None
#             },
#             {
#                 'code': 'duplicate-header',
#                 'column-number': 4,
#                 'message': 'Header in column 4 is duplicated to ...',
#                 'row': None,
#                 'row-number': None
#             },
#         ],
#         'headers': ['name', 'ward', 'party', 'other'],
#         'row-count': 79,
#         'place': 'http://example.com/invalid.csv',
#         'time': 0.007,
#         'valid': False,
#     }],
#     'time': 0.009,
#     'valid': False,
#     'warnings': [],
# }
INVALID_REPORT = {
    "valid": False,
    "stats": {"tasks": 1, "errors": 1, "warnings": 0, "seconds": 0.004},
    "warnings": [],
    "errors": [],
    "tasks": [{
        "name": "4e-81c0-454e-9255-01bf50b096bb",
        "type": "table",
        "valid": False,
        "place": "http://example.com/invalid.csv",
        "labels": ["a", "b", "c", "d"],
        "stats": {
            "errors": 1, "warnings": 0, "seconds": 0.004,
            "md5": "c451d87466e423fd10693865caeaa730",
            "sha256": "b80b3082c86083ab623622bf299a17c793037fd5d3bbf0cdbca0c0438417de5a",
            "bytes": 14,
            "fields": 4,
            "rows": 1
        },
        "warnings": [],
        "errors": [{
            "type": "missing-cell",
            "title": "Missing Cell",
            "description": "This row has less values compared to the header row (the first row in the data source). A key concept is that all the rows in tabular data must have the same number of columns.",
            "message": "Row at position \"2\" has a missing cell in field \"d\" at position \"4\"",
            "tags": ["#table", "#row", "#cell"],
            "note": "",
            "cells": ["1", "2", "3"],
            "rowNumber": 2,
            "cell": "",
            "fieldName": "d",
            "fieldNumber": 4
        }]
    }]
}

# GOODTABLES_ERROR_REPORT = {
#     'error-count': 0,
#     'table-count': 0,
#     'warnings': ['Some warning'],
# }
ERROR_REPORT = {
    "valid": False,
    "stats": {"tasks": 1, "errors": 1, "warnings": 0, "seconds": 0.003},
    "warnings": [],
    "errors": [],
    "tasks": [
        {
            "name": "file", "type": "table", "valid": False, "place": "http://example.com/file.csv", "labels": [],
            "stats": {"errors": 1, "warnings": 0, "seconds": 0.003, "md5": "d41d8cd98f00b204e9800998ecf8427e",
                      "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"},
            "warnings": [],
            "errors": [{
                "type": "source-error",
                "title": "Source Error",
                "description": "Data reading error because of not supported or inconsistent contents.",
                "message": "The data source has not supported or has inconsistent contents: the source is empty",
                "tags": [], "note": "the source is empty"
            }]
        }
    ]
}


class MockFileStorage(FileStorage):
    pass
