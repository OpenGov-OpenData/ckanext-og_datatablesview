# -*- coding: utf-8 -*-
from flask import Blueprint

import ckan.plugins as p
import ckanext.og_datatablesview.utils as utils


class MixinPlugin(p.SingletonPlugin):
    p.implements(p.IBlueprint)

    # IBlueprint
    def get_blueprint(self):
        return api


def ajax(resource_view_id):
    return utils.ajax(resource_view_id)


def filtered_download(resource_view_id):
    return utils.filtered_download(resource_view_id)


api = Blueprint('datatablesview', __name__)
api.add_url_rule('/datatables/ajax/<resource_view_id>', view_func=ajax, methods=[u'POST'])
api.add_url_rule('/datatables/filtered-download/<resource_view_id>', view_func=filtered_download, methods=[u'POST'])
