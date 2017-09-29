from ckantoolkit import config, asbool


def get_update_mode_from_config():
    if asbool(
            config.get(u'ckanext.validation.run_on_update_sync', False)):
        return u'sync'
    elif asbool(
            config.get(u'ckanext.validation.run_on_update_async', True)):
        return u'async'
    else:
        return None


def get_create_mode_from_config():
    if asbool(
            config.get(u'ckanext.validation.run_on_create_sync', False)):
        return u'sync'
    elif asbool(
            config.get(u'ckanext.validation.run_on_create_async', True)):
        return u'async'
    else:
        return None
