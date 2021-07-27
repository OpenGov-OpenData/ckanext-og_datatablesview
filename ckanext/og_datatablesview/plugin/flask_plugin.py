# -*- coding: utf-8 -*-

import ckan.plugins as p
import ckanext.og_datatablesview.blueprint as blueprint


class MixinPlugin(p.SingletonPlugin):
    p.implements(p.IBlueprint)

    # IBlueprint
    def get_blueprint(self):
        return blueprint.ogdatatablesview
