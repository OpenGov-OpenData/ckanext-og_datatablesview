import pytest

import ckan.plugins as p
from ckan.tests import factories
import ckanext.og_datatablesview.utils as test_utils


@pytest.mark.usefixtures("clean_db")
class TestUtils:

    def test_og_datatableview_on_resource_page_success(self):
        sysadmin = factories.Sysadmin()
        dataset = factories.Dataset()
        resource = factories.Resource(
            package_id=dataset['id'],
            url='https://cloudcity.ogopendata.com/dataset/e8350e79-172a-4dca-b971-362380f81332/resource/3626b679-5bde-4582-bc0b-ff2ac66cf440/download/approved-building-permits_analyze-boston.csv',
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


    def test_og_datatableview_on_resource_page_failure(self):
        sysadmin = factories.Sysadmin()
        dataset = factories.Dataset()
        resource = factories.Resource(
            package_id=dataset['id'],
            url='https://cloudcity.ogopendata.com/dataset/e8350e79-172a-4dca-b971-362380f81332/resource/3626b679-5bde-4582-bc0b-ff2ac66cf440/download/approved-building-permits_analyze-boston.csv',
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

        assert not response.get('title') == 'Data Tables'
        assert not response.get('view_type') == 'datatables_view'


    def test_og_datatableview_display_copy_button_success(self):
        sysadmin = factories.Sysadmin()
        dataset = factories.Dataset()
        resource = factories.Resource(
            package_id=dataset['id'],
            url='https://cloudcity.ogopendata.com/dataset/e8350e79-172a-4dca-b971-362380f81332/resource/3626b679-5bde-4582-bc0b-ff2ac66cf440/download/approved-building-permits_analyze-boston.csv',
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


    def test_og_datatableview_display_copy_button_failure(self):
        sysadmin = factories.Sysadmin()
        dataset = factories.Dataset()
        resource = factories.Resource(
            package_id=dataset['id'],
            url='https://cloudcity.ogopendata.com/dataset/e8350e79-172a-4dca-b971-362380f81332/resource/3626b679-5bde-4582-bc0b-ff2ac66cf440/download/approved-building-permits_analyze-boston.csv',
            format='CSV'
        )
        resource_view = factories.ResourceView(
            resource_id=resource['id'],
            title='OG Data Tables',
            view_type='og_datatables_view',
            copy_print_buttons=False
        )

        response = p.toolkit.get_action('resource_view_show')(
            {'user': sysadmin.get('name')},
            {'id': resource_view.get('id')}
        )

        assert response.get('copy_print_buttons') == False


    def test_og_datatableview_display_export_button_success(self):
        sysadmin = factories.Sysadmin()
        dataset = factories.Dataset()
        resource = factories.Resource(
            package_id=dataset['id'],
            url='https://cloudcity.ogopendata.com/dataset/e8350e79-172a-4dca-b971-362380f81332/resource/3626b679-5bde-4582-bc0b-ff2ac66cf440/download/approved-building-permits_analyze-boston.csv',
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


    def test_og_datatableview_display_export_button_failure(self):
        sysadmin = factories.Sysadmin()
        dataset = factories.Dataset()
        resource = factories.Resource(
            package_id=dataset['id'],
            url='https://cloudcity.ogopendata.com/dataset/e8350e79-172a-4dca-b971-362380f81332/resource/3626b679-5bde-4582-bc0b-ff2ac66cf440/download/approved-building-permits_analyze-boston.csv',
            format='CSV'
        )
        resource_view = factories.ResourceView(
            resource_id=resource['id'],
            title='OG Data Tables',
            view_type='og_datatables_view',
            export_button=False
        )

        response = p.toolkit.get_action('resource_view_show')(
            {'user': sysadmin.get('name')},
            {'id': resource_view.get('id')}
        )

        assert response.get('export_button') == False

    def test_og_datatableview_custom_options_success(self):
        sysadmin = factories.Sysadmin()
        dataset = factories.Dataset()
        resource = factories.Resource(
            package_id=dataset['id'],
            url='https://cloudcity.ogopendata.com/dataset/e8350e79-172a-4dca-b971-362380f81332/resource/3626b679-5bde-4582-bc0b-ff2ac66cf440/download/approved-building-permits_analyze-boston.csv',
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


    def test_og_datatableview_custom_options_failure(self):
        sysadmin = factories.Sysadmin()
        dataset = factories.Dataset()
        resource = factories.Resource(
            package_id=dataset['id'],
            url='https://cloudcity.ogopendata.com/dataset/e8350e79-172a-4dca-b971-362380f81332/resource/3626b679-5bde-4582-bc0b-ff2ac66cf440/download/approved-building-permits_analyze-boston.csv',
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

        assert response.get('export_button') != False
        assert response.get('responsive') != False
        assert response.get('copy_print_buttons') != True
        assert response.get('col_reorder') != True


    def test_og_datatableview_change_show_columns_success(self):
        sysadmin = factories.Sysadmin()
        dataset = factories.Dataset()
        resource = factories.Resource(
            package_id=dataset['id'],
            url='https://cloudcity.ogopendata.com/dataset/e8350e79-172a-4dca-b971-362380f81332/resource/3626b679-5bde-4582-bc0b-ff2ac66cf440/download/approved-building-permits_analyze-boston.csv',
            format='CSV'
        )
        resource_view = factories.ResourceView(
            resource_id=resource['id'],
            title='OG Data Tables',
            view_type='og_datatables_view',
            show_fields= [
                "permitnumber",
                "worktype",
                "permittypedescr",
                "description",
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
            "permitnumber",
            "worktype",
            "permittypedescr",
            "description",
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


    def test_og_datatableview_change_show_columns_failure(self):
        sysadmin = factories.Sysadmin()
        dataset = factories.Dataset()
        resource = factories.Resource(
            package_id=dataset['id'],
            url='https://cloudcity.ogopendata.com/dataset/e8350e79-172a-4dca-b971-362380f81332/resource/3626b679-5bde-4582-bc0b-ff2ac66cf440/download/approved-building-permits_analyze-boston.csv',
            format='CSV'
        )
        resource_view = factories.ResourceView(
            resource_id=resource['id'],
            title='OG Data Tables',
            view_type='og_datatables_view',
            show_fields= [
                "permitnumber",
                "worktype",
                "permittypedescr",
                "description",
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

        assert response.get('show_fields') != [
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

