# encoding: utf-8

import ckan.plugins as p
import ckan.plugins.toolkit as toolkit
import ckan.lib.navl.dictization_functions as df
import ckanext.og_datatablesview.helpers as helpers
from ckanext.og_datatablesview import blueprint

missing = df.missing

default = toolkit.get_validator(u'default')
boolean_validator = toolkit.get_validator(u'boolean_validator')
natural_number_validator = toolkit.get_validator(u'natural_number_validator')
ignore_missing = toolkit.get_validator(u'ignore_missing')

DEFAULT_PAGE_LENGTH_CHOICES = '25 50 100 500'


class OG_DataTablesView(p.SingletonPlugin):
    u'''
    DataTables table view plugin
    '''
    p.implements(p.IConfigurer, inherit=True)
    p.implements(p.IResourceView, inherit=True)
    p.implements(p.IBlueprint)
    p.implements(p.IValidators)
    p.implements(p.ITemplateHelpers)

    # IBlueprint

    def get_blueprint(self):
        return blueprint.ogdatatablesview

    # IConfigurer

    def update_config(self, config):
        u'''
        Set up the resource library, public directory and
        template directory for the view
        '''

        self.responsive_button_def = toolkit.asbool(
            config.get(u'ckan.datatables.view_table_responsive_default', False))
        self.col_unhide_button_def = toolkit.asbool(
            config.get(u'ckan.datatables.view_table_columnhide_default', True))
        self.export_button_def = toolkit.asbool(
            config.get(u'ckan.datatables.view_table_displayexport_default', False))
        self.copy_print_buttons_def = toolkit.asbool(
            config.get(u'ckan.datatables.view_table_displaycopyprint_default', False))
        self.col_reorder_def = toolkit.asbool(
            config.get(u'ckan.datatables.view_table_colreorder_default', True))

        # https://datatables.net/reference/option/lengthMenu
        self.page_length_choices = toolkit.aslist(
            config.get(
                u'ckan.datatables.page_length_choices',
                DEFAULT_PAGE_LENGTH_CHOICES
            )
        )
        self.page_length_choices = [int(i) for i in self.page_length_choices]
        self.state_saving = config.get(u'ckan.datatables.state_saving', True)

        # https://datatables.net/reference/option/stateDuration
        self.state_duration = config.get(
            u"ckan.datatables.state_duration", 7200)
        self.data_dictionary_labels = config.get(
            u"ckan.datatables.data_dictionary_labels", False)
        self.ellipsis_length = config.get(
            u"ckan.datatables.ellipsis_length", 0)
        self.date_format = config.get(u"ckan.datatables.date_format", "llll")
        self.default_view = config.get(u"ckan.datatables.default_view", "table")

        toolkit.add_template_directory(config, u'templates')
        toolkit.add_public_directory(config, u'assets')
        toolkit.add_resource(u'assets', u'ckanext-og_datatablesview')

    # IResourceView

    def can_view(self, data_dict):
        resource = data_dict['resource']
        return resource.get(u'datastore_active')

    def setup_template_variables(self, context, data_dict):
        return {u'page_length_choices': self.page_length_choices,
                u'state_saving': self.state_saving,
                u'state_duration': self.state_duration,
                u'data_dictionary_labels': self.data_dictionary_labels,
                u'ellipsis_length': self.ellipsis_length,
                u'date_format': self.date_format,
                u'default_view': self.default_view}

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
        data_dict['resource_view']['col_unhide_button_def'] = self.col_unhide_button_def
        data_dict['resource_view']['export_button_def'] = self.export_button_def
        data_dict['resource_view']['copy_print_buttons_def'] = self.copy_print_buttons_def
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
            u'preview_enabled': False,
            u'schema': {
                # The root of the problem here is that this info(self) method is called on two different scenarios:
                # 1. When the user is creating/updating a view with their browser (form_template method)
                # 2. When ckan is creating a new view from a resource that was just uploaded (ckan.views.default_views)

                # Why we cannot use the default(True) validator here:
                # When the web user unchecks the checkbox and saves, the browser POSTs a null value for 
                # that key, so: if the user unchecked the checkbox and saved, the value will be null
                # and if we have default(True) validator, it will be set to True, as the 
                # validator will replace the null value with true, which is the opposite of what the user wanted 
                # (The CRD that started this issue)

                # We also cannot use the default(False) validator here, 
                # When you upload a new csv, ckan will automatically create a DataTable view using this info() method
                # and we need it to use the configurable values when that happens, not a hardcoded value. The problem 
                # there is, when the view is being created by ckan, it doesn't use the form_template() method above,
                # so the configurable defaults are not being followed. 
                
                # The only way to fix both problems is writing our own validator, because Null means either the user 
                # unchecked the checkbox or the view is being created by ckan. If it was the user, it should be false, 
                # if it was CKAN, it should be the default value by configuration.
                u'responsive': [configurabledefaults_validator(self.responsive_button_def), boolean_validator],
                u'col_unhide_button': [configurabledefaults_validator(self.col_unhide_button_def), boolean_validator],
                u'export_button': [configurabledefaults_validator(self.export_button_def), boolean_validator],
                u'copy_print_buttons': [configurabledefaults_validator(self.copy_print_buttons_def), boolean_validator],
                u'col_reorder': [configurabledefaults_validator(self.col_reorder_def), boolean_validator],
                u'ellipsis_length': [default(self.ellipsis_length),
                                     natural_number_validator],
                u'date_format': [default(self.date_format)],
                u'show_fields': [ignore_missing],
                u'sort_column': [ignore_missing],
                u'sort_order': [ignore_missing],
                u'filterable': [default(True), boolean_validator],
            }
        }

    # IValidators

    def get_validators(self):
        return {
            'configurabledefaults_validator': configurabledefaults_validator,
        }

    # ITemplateHelpers

    def get_helpers(self):
        return {
            'og_datatablesview_null_label': helpers.og_datatablesview_null_label,
            'og_datastore_dictionary': helpers.og_datastore_dictionary,
        }


def configurabledefaults_validator(default_configurable_value):
    def callable(key, data, errors, context):
        # looking at the "for_view" property we can determine if the view is being created 
        # by the internal default view mechanism or by the user's browser
        if context.get('for_view'):
            # This means the user is creating/editing the view with their browser
            # so we set the values chosen by the user, 
            if data.get(key) is missing or data.get(key) is None or data.get(key) == '':
                # When the web user unchecks the checkbox and saves, 
                # the browser POSTs a null value, so we set it to False
                data[key] = False
        else:
            # the view is being created by the default view mechanism, 
            # so we set the values following the configurable defaults
            data[key] = default_configurable_value
    return callable
