# encoding: utf-8

from ckantoolkit import BaseController

from ckanext.validation import common


class ValidationController(BaseController):

    def validation(self, resource_id):
        return common.validation(resource_id)
