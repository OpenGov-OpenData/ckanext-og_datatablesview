# -*- coding: utf-8 -*-
from flask import Blueprint

import ckan.plugins as p
from ckanext.og_datatablesview.controller import DataTablesController


class MixinPlugin(p.SingletonPlugin):
    p.implements(p.IBlueprint)

    # IBlueprint
    def get_blueprint(self):
        return api


def ajax():
    return DataTablesController().ajax()


def filtered_download():
    return DataTablesController().filtered_download()


api = Blueprint('datatablesview', __name__)
api.add_url_rule('/datatables/ajax/<resource_view_id>', view_func=ajax, methods=[u'POST'])
api.add_url_rule('/datatables/filtered-download/<resource_view_id>', view_func=filtered_download, methods=[u'POST'])
