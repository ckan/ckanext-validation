# encoding: utf-8

from flask import Blueprint

from ckanext.validation import common

validation = Blueprint(u'validation', __name__)

validation.add_url_rule(
    u'/dataset/<id>/resource/<resource_id>/validation', 'read', methods=('GET',), view_func=common.validation
)


def get_blueprints():
    return [validation]
