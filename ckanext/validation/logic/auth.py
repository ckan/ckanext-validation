import ckan.plugins.toolkit as tk


def get_auth_functions():
    validators = (
        resource_validation_run,
        resource_validation_delete,
        resource_validation_show,
        resource_validation_run_batch,
    )

    return {"{}".format(func.__name__): func for func in validators}


def resource_validation_run(context, data_dict):
    if tk.check_access(u'resource_update', context,
                       {u'id': data_dict[u'resource_id']}):
        return {u'success': True}
    return {u'success': False}


def resource_validation_delete(context, data_dict):
    if tk.check_access(u'resource_update', context,
                       {u'id': data_dict[u'resource_id']}):
        return {u'success': True}
    return {u'success': False}


@tk.auth_allow_anonymous_access
def resource_validation_show(context, data_dict):
    if tk.check_access(u'resource_show', context,
                       {u'id': data_dict[u'resource_id']}):
        return {u'success': True}
    return {u'success': False}


def resource_validation_run_batch(context, data_dict):
    '''u Sysadmins only'''
    return {u'success': False}
