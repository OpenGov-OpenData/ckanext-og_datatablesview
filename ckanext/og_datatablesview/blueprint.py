# encoding: utf-8

from flask import Blueprint

import ckanext.og_datatablesview.utils as utils


ogdatatablesview = Blueprint(u'ogdatatablesview', __name__)


def ajax(resource_view_id):
    return utils.ajax(resource_view_id)

def filtered_download(resource_view_id):
    return utils.filtered_download(resource_view_id)


ogdatatablesview.add_url_rule(
    u'/og_datatables/ajax/<resource_view_id>',
    view_func=ajax, methods=[u'POST']
)

ogdatatablesview.add_url_rule(
    u'/og_datatables/filtered-download/<resource_view_id>',
    view_func=filtered_download, methods=[u'POST']
)
