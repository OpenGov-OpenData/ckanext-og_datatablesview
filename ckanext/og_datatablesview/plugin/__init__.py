# encoding: utf-8

import ckan.plugins as p
import ckan.plugins.toolkit as toolkit
from ckan.exceptions import CkanVersionException

from ckanext.og_datatablesview.helpers import version_builder

try:
    toolkit.requires_ckan_version("2.9")
except CkanVersionException:
    from ckanext.og_datatablesview.plugin.pylons_plugin import MixinPlugin
else:
    from ckanext.og_datatablesview.plugin.flask_plugin import MixinPlugin


default = toolkit.get_validator(u'default')
boolean_validator = toolkit.get_validator(u'boolean_validator')
ignore_missing = toolkit.get_validator(u'ignore_missing')

# see https://datatables.net/examples/advanced_init/length_menu.html
DEFAULT_PAGE_LENGTH_CHOICES = '10 25 50 100'


class OG_DataTablesView(MixinPlugin):
    '''
    DataTables table view plugin
    '''
    p.implements(p.IConfigurer, inherit=True)
    p.implements(p.IResourceView, inherit=True)
    p.implements(p.ITemplateHelpers)

    # IConfigurer
    def update_config(self, config):
        '''
        Set up the resource library, public directory and
        template directory for the view
        '''

        self.responsive_button_def = toolkit.asbool(
            config.get(u'ckan.datatables.view_table_responsive_default', False))
        self.copy_print_buttons_def = toolkit.asbool(
            config.get(u'ckan.datatables.view_table_displaycopyprint_default', False))
        self.export_button_def = toolkit.asbool(
            config.get(u'ckan.datatables.view_table_displayexport_default', False))
        self.col_reorder_def = toolkit.asbool(
            config.get(u'ckan.datatables.view_table_colreorder_default', True))
        
        # https://datatables.net/reference/option/lengthMenu
        self.page_length_choices = toolkit.aslist(
            config.get(u'ckan.datatables.page_length_choices',
                       DEFAULT_PAGE_LENGTH_CHOICES))
        self.page_length_choices = [int(i) for i in self.page_length_choices]

        toolkit.add_template_directory(config, u'../templates')
        toolkit.add_public_directory(config, u'../assets')
        toolkit.add_resource('../assets', u'ckanext-og_datatablesview')

    # IResourceView
    def can_view(self, data_dict):
        resource = data_dict['resource']
        return resource.get(u'datastore_active')

    def setup_template_variables(self, context, data_dict):
        return {u'page_length_choices': self.page_length_choices}

    def view_template(self, context, data_dict):
        resource_view = data_dict.get('resource_view')
        sort_column = resource_view.get('sort_column')
        show_fields = resource_view.get('show_fields', [])
        # Set the index of the sort column if it's displayed
        if sort_column in show_fields:
            sort_index = show_fields.index(sort_column)
            data_dict['resource_view']['sort_index'] = sort_index
        return u'og_datatables/datatables_view.html'

    def form_template(self, context, data_dict):
        data_dict['resource_view']['responsive_button_def'] = self.responsive_button_def
        data_dict['resource_view']['copy_print_buttons_def'] = self.copy_print_buttons_def
        data_dict['resource_view']['export_button_def'] = self.export_button_def
        data_dict['resource_view']['col_reorder_def'] = self.col_reorder_def
        return u'og_datatables/datatables_form.html'

    def info(self):
        return {
            u'name': u'og_datatables_view',
            u'title': u'Data Table',
            u'filterable': True,
            u'icon': u'table',
            u'requires_datastore': True,
            u'default_title': p.toolkit._(u'Data Table'),
            u'schema': {
                u'responsive': [default(False), boolean_validator],
                u'export_button': [default(False), boolean_validator],
                u'copy_print_buttons': [default(False), boolean_validator],
                # We cannot use default(True) here, as the browser POSTs a null value when user unchecks the checkbox
                u'col_reorder': [default(False), boolean_validator],
                u'show_fields': [ignore_missing],
                u'sort_column': [ignore_missing],
                u'sort_order': [ignore_missing],
                u'filterable': [default(True), boolean_validator]
            }
        }

    # ITemplateHelpers
    def get_helpers(self):
        return {
            'version': version_builder,
        }
