# -*- coding: utf-8 -*-
from flask import Blueprint

import ckan.plugins as p
import ckanext.og_datatablesview.utils as utils


class MixinPlugin(p.SingletonPlugin):
    p.implements(p.IBlueprint)

    # IBlueprint
    def get_blueprint(self):
        return datatablesview


def ajax(resource_view_id):
    return utils.ajax(resource_view_id)


def filtered_download(resource_view_id):
    return utils.filtered_download(resource_view_id)


datatablesview = Blueprint(u'datatablesview', __name__)
datatablesview.add_url_rule(u'/datatables/ajax/<resource_view_id>', view_func=ajax, methods=[u'POST'])
datatablesview.add_url_rule(u'/datatables/filtered-download/<resource_view_id>', view_func=filtered_download, methods=[u'POST'])
