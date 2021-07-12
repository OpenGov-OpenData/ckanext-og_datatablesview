# -*- coding: utf-8 -*-

import ckan.plugins as p


class MixinPlugin(p.SingletonPlugin):
    p.implements(p.IRoutes, inherit=True)

    # IRoutes
    def before_map(self, map):
        map.connect(
            'ogdatatablesview.ajax',
            u'/og_datatables/ajax/{resource_view_id}',
            controller=u'ckanext.og_datatablesview.controller:DataTablesController',
            action=u'ajax')
        map.connect(
            'ogdatatablesview.filtered_download',
            u'/og_datatables/filtered-download/{resource_view_id}',
            controller=u'ckanext.og_datatablesview.controller:DataTablesController',
            action=u'filtered_download')
        return map
