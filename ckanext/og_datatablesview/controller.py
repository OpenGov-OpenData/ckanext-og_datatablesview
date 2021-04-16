# encoding: utf-8

from ckan.lib.base import BaseController

import ckanext.og_datatablesview.utils as utils


class DataTablesController(BaseController):
    def ajax(self, resource_view_id):
        return utils.ajax(resource_view_id)

    def filtered_download(self, resource_view_id):
        return utils.filtered_download(resource_view_id)
