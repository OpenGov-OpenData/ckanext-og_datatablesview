# -*- coding: utf-8 -*-

from flask import Blueprint

import ckan.plugins as p
import ckanext.og_datatablesview.utils as utils


ogdatatablesview = Blueprint(u'ogdatatablesview', __name__)


class MixinPlugin(p.SingletonPlugin):
    p.implements(p.IBlueprint)

    # IBlueprint
    def get_blueprint(self):
        return ogdatatablesview


def ajax(resource_view_id):
    return utils.ajax(resource_view_id)

def filtered_download(resource_view_id):
    return utils.filtered_download(resource_view_id)


ogdatatablesview.add_url_rule(
    u'/datatables/ajax/<resource_view_id>',
    view_func=ajax, methods=[u'POST']
)
ogdatatablesview.add_url_rule(
    u'/datatables/filtered-download/<resource_view_id>',
    view_func=filtered_download, methods=[u'POST']
)
