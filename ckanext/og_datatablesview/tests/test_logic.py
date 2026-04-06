import pytest

import ckan.plugins.toolkit as toolkit
from ckan.tests import factories
from ckanext.og_datatablesview.blueprint import format_fts_query


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

        response = toolkit.get_action('resource_view_show')(
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
            copy_print_buttons=False
        )

        response = toolkit.get_action('resource_view_show')(
            {'user': sysadmin.get('name')},
            {'id': resource_view.get('id')}
        )

        assert response.get('copy_print_buttons') == False


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
            export_button=False
        )

        response = toolkit.get_action('resource_view_show')(
            {'user': sysadmin.get('name')},
            {'id': resource_view.get('id')}
        )

        assert response.get('export_button') == False


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
            export_button=False,
            responsive=False,
            copy_print_buttons=False,
            col_reorder=True

        )

        response = toolkit.get_action('resource_view_show')(
            {'user': sysadmin.get('name')},
            {'id': resource_view.get('id')}
        )

        assert response.get('export_button') == False
        assert response.get('responsive') == False
        assert response.get('copy_print_buttons') == False
        assert response.get('col_reorder') == True


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

        response = toolkit.get_action('resource_view_show')(
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

        resource_view_delete_response = toolkit.get_action('resource_view_delete')(
            {'user': sysadmin.get('name')},
            {'id': resource_view_id}
        )

        with pytest.raises(toolkit.ObjectNotFound):
            resource_view_show_response = toolkit.get_action('resource_view_show')(
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

        resource_view_update_response = toolkit.get_action('resource_view_update')(
            {'user': sysadmin.get('name')},
            {'id': resource_view_1.get('id'), 'description': 'Testing resource view update'},
        )

        response_1 = toolkit.get_action('resource_view_show')(
            {'user': sysadmin.get('name')},
            {'id': resource_view_1.get('id')}
        )

        response_2 = toolkit.get_action('resource_view_show')(
            {'user': sysadmin.get('name')},
            {'id': resource_view_2.get('id')}
        )

        assert response_1.get('description') == 'Testing resource view update'
        assert response_1.get('description') != response_2.get('description')


    def test_og_datatableview_hide_resource_info_true_success(self):
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
            hide_resource_info=True
        )

        response = toolkit.get_action('resource_view_show')(
            {'user': sysadmin.get('name')},
            {'id': resource_view.get('id')}
        )

        assert response.get('hide_resource_info') == True


    def test_og_datatableview_hide_resource_info_false_success(self):
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
            hide_resource_info=False
        )

        response = toolkit.get_action('resource_view_show')(
            {'user': sysadmin.get('name')},
            {'id': resource_view.get('id')}
        )

        assert response.get('hide_resource_info') == False


    def test_og_datatableview_hide_resource_info_default_false_success(self):
        """Test that hide_resource_info defaults to False when not specified"""
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

        response = toolkit.get_action('resource_view_show')(
            {'user': sysadmin.get('name')},
            {'id': resource_view.get('id')}
        )

        assert response.get('hide_resource_info') == False


    def test_og_datatableview_hide_resource_info_with_other_options_success(self):
        """Test hide_resource_info works correctly with other configuration options"""
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
            hide_resource_info=True,
            export_button=False,
            responsive=True,
            copy_print_buttons=False,
            col_reorder=True
        )

        response = toolkit.get_action('resource_view_show')(
            {'user': sysadmin.get('name')},
            {'id': resource_view.get('id')}
        )

        assert response.get('hide_resource_info') == True
        assert response.get('export_button') == False
        assert response.get('responsive') == True
        assert response.get('copy_print_buttons') == False
        assert response.get('col_reorder') == True


    def test_og_datatableview_update_hide_resource_info_success(self):
        """Test updating hide_resource_info on an existing view"""
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
            hide_resource_info=False
        )

        # Update to hide resource info
        toolkit.get_action('resource_view_update')(
            {'user': sysadmin.get('name')},
            {'id': resource_view.get('id'), 'hide_resource_info': True}
        )

        response = toolkit.get_action('resource_view_show')(
            {'user': sysadmin.get('name')},
            {'id': resource_view.get('id')}
        )

        assert response.get('hide_resource_info') == True


class TestFormatFtsQuery:

    def test_format_fts_query_empty_string(self):
        assert format_fts_query('') == ''

    def test_format_fts_query_single_word(self):
        assert format_fts_query('test') == 'test:*'

    def test_format_fts_query_multiple_words(self):
        assert format_fts_query('test query') == 'test:* & query:*'

    def test_format_fts_query_apostrophe_compound_word(self):
        # Apostrophe creates compound word - should use OR for parts
        result = format_fts_query("L'est")
        assert result == '(L:* | est:*)'

    def test_format_fts_query_slash_compound_word(self):
        # Slash creates compound word - should use OR for parts
        result = format_fts_query('Board/Village')
        assert result == '(Board:* | Village:*)'

    def test_format_fts_query_mixed_words_and_compound(self):
        # Mix of regular words and compound words
        result = format_fts_query('Orleans Parish School Board/Village')
        assert result == 'Orleans:* & Parish:* & School:* & (Board:* | Village:*)'

    def test_format_fts_query_apostrophe_in_phrase(self):
        # Apostrophe in middle of phrase
        result = format_fts_query("De L'est Elementary")
        assert result == 'De:* & (L:* | est:*) & Elementary:*'

    def test_format_fts_query_complex_search(self):
        # Complex search with multiple compound words
        result = format_fts_query("Orleans Parish School Board/Village De L'est Elementary School")
        assert result == 'Orleans:* & Parish:* & School:* & (Board:* | Village:*) & De:* & (L:* | est:*) & Elementary:* & School:*'

    def test_format_fts_query_special_characters(self):
        # Other special characters should be replaced with underscore
        result = format_fts_query('test@example.com')
        assert result == '(test:* | example:* | com:*)'

    def test_format_fts_query_hyphens_preserved(self):
        # Hyphens should be preserved
        result = format_fts_query('test-word')
        assert result == 'test-word:*'

    def test_format_fts_query_multiple_apostrophes(self):
        # Multiple apostrophes
        result = format_fts_query("O'Brien's")
        assert result == "(O:* | Brien:* | s:*)"

    def test_format_fts_query_date_single_digit_month_day(self):
        # Date with single digit month and day
        result = format_fts_query('1/3/2025')
        assert result == '1/3/2025:*'

    def test_format_fts_query_date_two_digit_month_day(self):
        # Date with two digit month and day
        result = format_fts_query('1/13/2025')
        assert result == '1/13/2025:*'

    def test_format_fts_query_date_two_digit_year(self):
        # Date with two digit year
        result = format_fts_query('1/13/25')
        assert result == '1/13/25:*'

    def test_format_fts_query_date_with_dash(self):
        # Date with dashes instead of slashes
        result = format_fts_query('1-13-2025')
        assert result == '1-13-2025:*'

    def test_format_fts_query_date_in_phrase(self):
        # Date within a phrase
        result = format_fts_query('Contract Begin Date 1/13/2025')
        assert result == 'Contract:* & Begin:* & Date:* & 1/13/2025:*'

    def test_format_fts_query_multiple_dates(self):
        # Multiple dates in search
        result = format_fts_query('1/13/2025 6/30/2025')
        assert result == '1/13/2025:* & 6/30/2025:*'

    def test_format_fts_query_date_with_compound_word(self):
        # Date with compound word in same search
        result = format_fts_query('Board/Village 1/13/2025')
        assert result == '(Board:* | Village:*) & 1/13/2025:*'
