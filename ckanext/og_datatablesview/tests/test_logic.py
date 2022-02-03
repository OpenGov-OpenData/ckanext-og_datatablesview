import pytest

import ckan.plugins as p
from ckan.tests import factories
import ckan.logic as logic
import ckanext.og_datatablesview.utils as test_utils


@pytest.mark.usefixtures("clean_db")
class TestUtils:

    def test_og_datatableview_on_resource_page_success(self):
        sysadmin = factories.Sysadmin()
        dataset = factories.Dataset()
        resource = factories.Resource(
            package_id=dataset['id'],
            format='CSV'
        )
        resource_view = factories.ResourceView(
            resource_id=resource['id'],
            title='OG Data Tables',
            view_type='og_datatables_view'
        )

        response = p.toolkit.get_action('resource_view_show')(
            {'user': sysadmin.get('name')},
            {'id': resource_view.get('id')}
        )

        assert response.get('title') == 'OG Data Tables'
        assert response.get('view_type') == 'og_datatables_view'


    def test_og_datatableview_display_copy_button_success(self):
        sysadmin = factories.Sysadmin()
        dataset = factories.Dataset()
        resource = factories.Resource(
            package_id=dataset['id'],
            format='CSV'
        )
        resource_view = factories.ResourceView(
            resource_id=resource['id'],
            title='OG Data Tables',
            view_type='og_datatables_view',
            copy_print_buttons=True
        )

        response = p.toolkit.get_action('resource_view_show')(
            {'user': sysadmin.get('name')},
            {'id': resource_view.get('id')}
        )

        assert response.get('copy_print_buttons') == True


    def test_og_datatableview_display_export_button_success(self):
        sysadmin = factories.Sysadmin()
        dataset = factories.Dataset()
        resource = factories.Resource(
            package_id=dataset['id'],
            format='CSV'
        )
        resource_view = factories.ResourceView(
            resource_id=resource['id'],
            title='OG Data Tables',
            view_type='og_datatables_view',
            export_button=True
        )

        response = p.toolkit.get_action('resource_view_show')(
            {'user': sysadmin.get('name')},
            {'id': resource_view.get('id')}
        )

        assert response.get('export_button') == True


    def test_og_datatableview_custom_options_success(self):
        sysadmin = factories.Sysadmin()
        dataset = factories.Dataset()
        resource = factories.Resource(
            package_id=dataset['id'],
            format='CSV'
        )
        resource_view = factories.ResourceView(
            resource_id=resource['id'],
            title='OG Data Tables',
            view_type='og_datatables_view',
            export_button=True,
            responsive=True,
            copy_print_buttons=False,
            col_reorder=False

        )

        response = p.toolkit.get_action('resource_view_show')(
            {'user': sysadmin.get('name')},
            {'id': resource_view.get('id')}
        )

        assert response.get('export_button') == True
        assert response.get('responsive') == True
        assert response.get('copy_print_buttons') == False
        assert response.get('col_reorder') == False


    def test_og_datatableview_change_show_columns_success(self):
        sysadmin = factories.Sysadmin()
        dataset = factories.Dataset()
        resource = factories.Resource(
            package_id=dataset['id'],
            format='CSV'
        )
        resource_view = factories.ResourceView(
            resource_id=resource['id'],
            title='OG Data Tables',
            view_type='og_datatables_view',
            show_fields= [
                "_id",
                "permitnumber",
                "worktype",
                "permittypedescr",
                "description",
                "comments",
                "applicant",
                "declared_valuation",
                "total_fees",
                "issued_date",
                "expiration_date",
                "status",
                "owner",
                "occupancytype",
                "sq_feet",
                "address",
                "city",
                "state",
                "zip",
                "property_id",
                "parcel_id",
                "location"
            ]
        )

        response = p.toolkit.get_action('resource_view_show')(
            {'user': sysadmin.get('name')},
            {'id': resource_view.get('id')}
        )

        assert response.get('show_fields') == [
            "_id",
            "permitnumber",
            "worktype",
            "permittypedescr",
            "description",
            "comments",
            "applicant",
            "declared_valuation",
            "total_fees",
            "issued_date",
            "expiration_date",
            "status",
            "owner",
            "occupancytype",
            "sq_feet",
            "address",
            "city",
            "state",
            "zip",
            "property_id",
            "parcel_id",
            "location"
        ]


    def test_og_datatableview_delete_resource_view_success(self):
        sysadmin = factories.Sysadmin()
        dataset = factories.Dataset()
        resource = factories.Resource(
            package_id=dataset['id'],
            format='CSV'
        )
        resource_view = factories.ResourceView(
            resource_id=resource['id'],
            title='OG Data Tables',
            view_type='og_datatables_view'
        )

        resource_view_id = resource_view.get('id')

        resource_view_delete_response = p.toolkit.get_action('resource_view_delete')(
            {'user': sysadmin.get('name')},
            {'id': resource_view_id}
        )

        with pytest.raises(logic.NotFound):
            resource_view_show_response = p.toolkit.get_action('resource_view_show')(
                {'user': sysadmin.get('name')},
                {'id': resource_view_id}
            )


    def test_og_datatableview_only_modify_one_view_success(self):
        sysadmin = factories.Sysadmin()
        dataset = factories.Dataset()
        resource = factories.Resource(
            package_id=dataset['id'],
            format='CSV'
        )
        resource_view_1 = factories.ResourceView(
            resource_id=resource['id'],
            title='OG Data Tables 1',
            view_type='og_datatables_view'
        )
        resource_view_2 = factories.ResourceView(
            resource_id=resource['id'],
            title='OG Data Tables 2',
            view_type='og_datatables_view'
        )

        resource_view_update_response = p.toolkit.get_action('resource_view_update')(
            {'user': sysadmin.get('name')},
            {'id': resource_view_1.get('id'), 'description': 'Testing resource view update'},
        )

        response_1 = p.toolkit.get_action('resource_view_show')(
            {'user': sysadmin.get('name')},
            {'id': resource_view_1.get('id')}
        )

        response_2 = p.toolkit.get_action('resource_view_show')(
            {'user': sysadmin.get('name')},
            {'id': resource_view_2.get('id')}
        )

        assert response_1.get('description') == 'Testing resource view update'
        assert response_1.get('description') != response_2.get('description')
