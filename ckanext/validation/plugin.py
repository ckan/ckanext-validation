import logging

import ckan.plugins as p
import ckan.plugins.toolkit as t


log = logging.getLogger(__name__)


class ValidationPlugin(p.SingletonPlugin):
    p.implements(p.IConfigurer)

    # IConfigurer

    def update_config(self, config_):
        t.add_template_directory(config_, 'templates')
        t.add_public_directory(config_, 'public')
        t.add_resource('fanstatic', 'validation')
