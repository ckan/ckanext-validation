# encoding: utf-8

from flask import Blueprint

from ckan.lib.navl.dictization_functions import unflatten
from ckan.logic import tuplize_dict, clean_dict, parse_params
from ckanext.validation.logic import is_tabular
from ckanext.validation.utils import turn_off_validation

from ckantoolkit import (
    c, g,
    NotAuthorized,
    ObjectNotFound,
    abort,
    _,
    render,
    get_action,
    request,
    config,
)


validation = Blueprint("validation", __name__)


def read(id, resource_id):

    try:
        validation = get_action(u"resource_validation_show")(
            {u"user": c.user}, {u"resource_id": resource_id}
        )

        resource = get_action(u"resource_show")({u"user": c.user}, {u"id": resource_id})

        dataset = get_action(u"package_show")(
            {u"user": c.user}, {u"id": resource[u"package_id"]}
        )

        # Needed for core resource templates
        c.package = c.pkg_dict = dataset
        c.resource = resource

        return render(
            u"validation/validation_read.html",
            extra_vars={
                u"validation": validation,
                u"resource": resource,
                u"dataset": dataset,
                u"pkg_dict": dataset,
            },
        )

    except NotAuthorized:
        abort(403, _(u"Unauthorized to read this validation report"))
    except ObjectNotFound:

        abort(404, _(u"No validation report exists for this resource"))

def _get_data():
    data = clean_dict(
	    unflatten(tuplize_dict(parse_params(request.form)))
    )
    data.update(clean_dict(
	    unflatten(tuplize_dict(parse_params(request.files)))
    ))
    return data


def resource_file_create(id):

    data_dict = _get_data()

    context = {
        'user': g.user,
    }
    data_dict["package_id"] = id

    with turn_off_validation():
        resource = get_action("resource_create")(context, data_dict)

        # If it's tabular (local OR remote), infer and store schema
        if is_tabular(filename=resource['url']):
            update_resource_schema = get_action('resource_table_schema_infer')(
                context, {'resource_id': resource['id'], 'store_schema': True}
            )
            resource['schema'] = update_resource_schema['schema']

    return resource


def resource_file_update(id, resource_id):
    # Get data from the request
    data_dict = _get_data()

    # Call resource_create
    context = {
        'user': g.user,
    }
    data_dict["id"] = resource_id
    data_dict["package_id"] = id

    with turn_off_validation():
        resource = get_action("resource_update")(context, data_dict)

        # If it's tabular (local OR remote), infer and store schema
        if is_tabular(resource['url']):
            resource_id = resource['id']
            update_resource_schema = get_action('resource_table_schema_infer')(
                context, {'resource_id': resource_id, 'store_schema': True}
            )
            resource['schema'] = update_resource_schema['schema']

    return resource

validation.add_url_rule(
    "/dataset/<id>/resource/<resource_id>/file", view_func=resource_file_update, methods=["POST"]
)

validation.add_url_rule(
    "/dataset/<id>/resource/file", view_func=resource_file_create, methods=["POST"]
)

validation.add_url_rule(
    "/dataset/<id>/resource/<resource_id>/validation", view_func=read
)
