# encoding: utf-8

from flask import Blueprint

from ckan.lib.navl.dictization_functions import unflatten
from ckan.logic import tuplize_dict, clean_dict, parse_params
from ckanext.validation.logic import is_tabular

from ckantoolkit import (
    c, g,
    NotAuthorized,
    ObjectNotFound,
    abort,
    _,
    render,
    get_action,
    request,
)
import ckantoolkit as t

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


def resource_file_create(id):

    # Get data from the request
    data_dict = _get_data()

    # Call resource_create
    # TODO: error handling
    context = {
        'user': g.user,
    }
    data_dict["package_id"] = id
    resource = get_action("resource_create")(context, data_dict)

    # If it's tabular (local OR remote), infer and store schema
    if is_tabular(resource):
        update_resource = get_action('resource_table_schema_infer')(
            context, {'resource_id': resource.id, 'store_schema': True}
        )

    # Return resource
    # TODO: set response format as JSON
    return resource


def resource_file_update(id, resource_id):
    # TODO: same as create, you can reuse as much code as needed
    pass


validation.add_url_rule(
    "/dataset/<id>/resource/file", view_func=resource_file_create, methods=["POST"]
)
validation.add_url_rule(
    "/dataset/<id>/resource/<resource_id>/file", view_func=resource_file_update, methods=["POST"]
)

validation.add_url_rule(
    "/dataset/<id>/resource/<resource_id>/validation", view_func=read
)
