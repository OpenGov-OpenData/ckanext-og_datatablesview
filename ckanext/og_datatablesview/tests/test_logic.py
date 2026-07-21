import pytest

import ckan.plugins.toolkit as toolkit
import ckan.lib.navl.dictization_functions as df
from ckan.tests import factories
from ckanext.og_datatablesview.plugin import (
    og_datatables_column_prefixes,
    og_datatables_column_suffixes,
)
from ckanext.og_datatablesview.helpers import og_datatablesview_is_numeric_column
from ckanext.og_datatablesview.blueprint import (
    format_fts_query,
    build_filter_where_fragments,
    build_fts_where_fragment,
    _quote_identifier,
    _quote_literal,
    _build_where_clause,
    _build_select_fields,
    _build_order_by,
)


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


    def test_og_datatableview_column_prefixes_dict_success(self):
        """A dict of column prefixes round-trips through the view config"""
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
            column_prefixes={'amount': '$', 'total_fees': '$'}
        )

        response = toolkit.get_action('resource_view_show')(
            {'user': sysadmin.get('name')},
            {'id': resource_view.get('id')}
        )

        assert response.get('column_prefixes') == {
            'amount': '$', 'total_fees': '$'
        }


    def test_og_datatableview_column_prefixes_default_empty_success(self):
        """column_prefixes is absent/empty when not specified"""
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

        assert not response.get('column_prefixes')


    def test_og_datatableview_column_suffixes_dict_success(self):
        """A dict of column suffixes round-trips through the view config"""
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
            column_suffixes={'amount': ' dollars', 'sq_feet': ' sqft'}
        )

        response = toolkit.get_action('resource_view_show')(
            {'user': sysadmin.get('name')},
            {'id': resource_view.get('id')}
        )

        assert response.get('column_suffixes') == {
            'amount': ' dollars', 'sq_feet': ' sqft'
        }


    def test_og_datatableview_column_suffixes_default_empty_success(self):
        """column_suffixes is absent/empty when not specified"""
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

        assert not response.get('column_suffixes')


    def test_og_datatableview_column_prefix_and_suffix_together_success(self):
        """Prefix and suffix are stored independently on the same view"""
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
            column_prefixes={'amount': '$'},
            column_suffixes={'amount': ' dollars'}
        )

        response = toolkit.get_action('resource_view_show')(
            {'user': sysadmin.get('name')},
            {'id': resource_view.get('id')}
        )

        assert response.get('column_prefixes') == {'amount': '$'}
        assert response.get('column_suffixes') == {'amount': ' dollars'}


class TestColumnPrefixesValidator:
    """Unit tests for the og_datatables_column_prefixes validator"""

    def test_missing_returns_empty(self):
        assert og_datatables_column_prefixes(df.missing) == {}

    def test_none_returns_empty(self):
        assert og_datatables_column_prefixes(None) == {}

    def test_empty_string_returns_empty(self):
        assert og_datatables_column_prefixes('') == {}

    def test_dict_passthrough(self):
        assert og_datatables_column_prefixes({'amount': '$'}) == {'amount': '$'}

    def test_json_string_decoded(self):
        # this is how the config form POSTs the value
        assert og_datatables_column_prefixes('{"amount": "$"}') == {'amount': '$'}

    def test_json_string_and_dict_normalise_identically(self):
        as_dict = og_datatables_column_prefixes({'a': '$', 'b': '#'})
        as_json = og_datatables_column_prefixes('{"a": "$", "b": "#"}')
        assert as_dict == as_json == {'a': '$', 'b': '#'}

    def test_blank_prefixes_dropped(self):
        assert og_datatables_column_prefixes(
            {'a': '$', 'b': '', 'c': None}
        ) == {'a': '$'}

    def test_invalid_json_returns_empty(self):
        assert og_datatables_column_prefixes('not json') == {}

    def test_non_dict_json_returns_empty(self):
        assert og_datatables_column_prefixes('[1, 2, 3]') == {}

    def test_values_coerced_to_str(self):
        assert og_datatables_column_prefixes({'a': 5}) == {'a': '5'}

    def test_xss_payload_stored_verbatim(self):
        # the validator stores the raw string; escaping happens at render time
        payload = '<img src=x onerror=alert(1)>'
        assert og_datatables_column_prefixes(
            {'a': payload}
        ) == {'a': payload}


class TestColumnSuffixesValidator:
    """Unit tests for the og_datatables_column_suffixes validator"""

    def test_missing_returns_empty(self):
        assert og_datatables_column_suffixes(df.missing) == {}

    def test_none_returns_empty(self):
        assert og_datatables_column_suffixes(None) == {}

    def test_empty_string_returns_empty(self):
        assert og_datatables_column_suffixes('') == {}

    def test_dict_passthrough(self):
        assert og_datatables_column_suffixes(
            {'amount': ' dollars'}
        ) == {'amount': ' dollars'}

    def test_json_string_decoded(self):
        # this is how the config form POSTs the value
        assert og_datatables_column_suffixes(
            '{"amount": " dollars"}'
        ) == {'amount': ' dollars'}

    def test_json_string_and_dict_normalise_identically(self):
        as_dict = og_datatables_column_suffixes({'a': ' kg', 'b': '%'})
        as_json = og_datatables_column_suffixes('{"a": " kg", "b": "%"}')
        assert as_dict == as_json == {'a': ' kg', 'b': '%'}

    def test_blank_suffixes_dropped(self):
        assert og_datatables_column_suffixes(
            {'a': ' kg', 'b': '', 'c': None}
        ) == {'a': ' kg'}

    def test_invalid_json_returns_empty(self):
        assert og_datatables_column_suffixes('not json') == {}

    def test_non_dict_json_returns_empty(self):
        assert og_datatables_column_suffixes('[1, 2, 3]') == {}

    def test_values_coerced_to_str(self):
        assert og_datatables_column_suffixes({'a': 5}) == {'a': '5'}

    def test_xss_payload_stored_verbatim(self):
        # the validator stores the raw string; escaping happens at render time
        payload = '<img src=x onerror=alert(1)>'
        assert og_datatables_column_suffixes(
            {'a': payload}
        ) == {'a': payload}


class TestIsNumericColumn:
    """Unit tests for the og_datatablesview_is_numeric_column helper"""

    @pytest.mark.parametrize('field_type', [
        'numeric', 'number', 'decimal', 'money',
        'int', 'integer', 'smallint', 'bigint',
        'int2', 'int4', 'int8',
        'float', 'float4', 'float8', 'real', 'double precision',
    ])
    def test_numeric_types_true(self, field_type):
        assert og_datatablesview_is_numeric_column(field_type) is True

    def test_case_insensitive(self):
        assert og_datatablesview_is_numeric_column('Int8') is True
        assert og_datatablesview_is_numeric_column('NUMERIC') is True
        assert og_datatablesview_is_numeric_column('MONEY') is True

    @pytest.mark.parametrize('field_type', [
        'text', 'timestamp', 'timestamptz', 'date', 'bool', 'json',
        '', None,
    ])
    def test_non_numeric_types_false(self, field_type):
        assert og_datatablesview_is_numeric_column(field_type) is False


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


class TestBuildFilterWhereFragments:

    def test_no_filters(self):
        null_clauses, regular_clauses = build_filter_where_fragments({})
        assert null_clauses == []
        assert regular_clauses == []

    def test_null_only(self):
        null_clauses, regular_clauses = build_filter_where_fragments(
            {'Status': ['']}
        )
        assert null_clauses == [
            '("Status" IS NULL OR "Status" = \'\')'
        ]
        assert regular_clauses == []

    def test_null_with_real_values(self):
        # Empty string plus real values for the same column
        null_clauses, regular_clauses = build_filter_where_fragments(
            {'Status': ['', 'Open', 'Closed']}
        )
        assert null_clauses == [
            '("Status" IS NULL OR "Status" = \'\' '
            'OR "Status" IN (\'Open\', \'Closed\'))'
        ]
        assert regular_clauses == []

    def test_single_regular_filter(self):
        null_clauses, regular_clauses = build_filter_where_fragments(
            {'Department': ['BTDT']}
        )
        assert null_clauses == []
        assert regular_clauses == ['"Department" = \'BTDT\'']

    def test_multiple_regular_filter_values_use_in(self):
        null_clauses, regular_clauses = build_filter_where_fragments(
            {'Department': ['BTDT', 'INFO']}
        )
        assert null_clauses == []
        assert regular_clauses == [
            '"Department" IN (\'BTDT\', \'INFO\')'
        ]

    def test_mixed_null_and_regular_filters(self):
        null_clauses, regular_clauses = build_filter_where_fragments(
            {'Status': [''], 'Department': ['BTDT']}
        )
        assert null_clauses == [
            '("Status" IS NULL OR "Status" = \'\')'
        ]
        assert regular_clauses == ['"Department" = \'BTDT\'']

    def test_scalar_value_normalised(self):
        null_clauses, regular_clauses = build_filter_where_fragments(
            {'Department': 'BTDT'}
        )
        assert regular_clauses == ['"Department" = \'BTDT\'']

    def test_identifier_escaping(self):
        # Double quotes in column name must be doubled
        null_clauses, _ = build_filter_where_fragments({'a"b': ['']})
        assert null_clauses == ['("a""b" IS NULL OR "a""b" = \'\')']

    def test_literal_escaping(self):
        # Single quotes in value must be doubled
        _, regular_clauses = build_filter_where_fragments(
            {'Name': ["O'Brien"]}
        )
        assert regular_clauses == ['"Name" = \'O\'\'Brien\'']

    def test_column_name_with_spaces(self):
        null_clauses, _ = build_filter_where_fragments(
            {'MPN Approval Status': ['']}
        )
        assert null_clauses == [
            '("MPN Approval Status" IS NULL '
            'OR "MPN Approval Status" = \'\')'
        ]


class TestBuildFtsWhereFragment:

    def test_no_search(self):
        assert build_fts_where_fragment({}, None) is None
        assert build_fts_where_fragment({}, '') is None

    def test_plain_query(self):
        result = build_fts_where_fragment({}, 'boston:*')
        assert result == "_full_text @@ to_tsquery('simple', 'boston:*')"

    def test_per_column_query(self):
        result = build_fts_where_fragment({'name': 'boston:*'}, None)
        assert result == (
            "to_tsvector('simple', cast(\"name\" as text)) "
            "@@ to_tsquery('simple', 'boston:*')"
        )

    def test_colsearch_takes_precedence_over_plain(self):
        result = build_fts_where_fragment({'name': 'boston:*'}, 'ignored:*')
        assert 'to_tsvector' in result
        assert 'ignored' not in result

    def test_per_column_multiple_columns(self):
        result = build_fts_where_fragment(
            {'name': 'a:*', 'city': 'b:*'}, None
        )
        assert (
            "to_tsvector('simple', cast(\"name\" as text)) "
            "@@ to_tsquery('simple', 'a:*')"
        ) in result
        assert (
            "to_tsvector('simple', cast(\"city\" as text)) "
            "@@ to_tsquery('simple', 'b:*')"
        ) in result
        assert ' AND ' in result

    def test_literal_escaping(self):
        result = build_fts_where_fragment({}, "o'brien:*")
        assert result == "_full_text @@ to_tsquery('simple', 'o''brien:*')"


class TestQuoting:

    def test_identifier_doubles_quotes(self):
        assert _quote_identifier('a"b') == '"a""b"'

    def test_identifier_strips_nul(self):
        # NUL bytes must be stripped, matching CKAN's postgres.identifier
        assert _quote_identifier('a\x00b') == '"ab"'

    def test_literal_doubles_single_quotes(self):
        assert _quote_literal("O'Brien") == "'O''Brien'"

    def test_literal_strips_nul(self):
        # NUL bytes must be stripped, matching CKAN's postgres.literal_string
        assert _quote_literal('a\x00b') == "'ab'"


class TestBuildWhereClause:

    def test_no_clauses_returns_true(self):
        assert _build_where_clause([], [], None) == '1=1'

    def test_combines_all_clauses_with_and(self):
        result = _build_where_clause(
            ['(x IS NULL)'], ['"d" = \'a\''], 'fts_frag'
        )
        assert result == "(x IS NULL) AND \"d\" = 'a' AND fts_frag"

    def test_skips_empty_fts_fragment(self):
        result = _build_where_clause(['(x IS NULL)'], [], None)
        assert result == '(x IS NULL)'


class TestBuildSelectFields:

    def test_quotes_each_column(self):
        assert _build_select_fields(['a', 'b c']) == '"a", "b c"'

    def test_empty_cols_returns_star(self):
        assert _build_select_fields([]) == '*'


class TestBuildOrderBy:

    def test_no_sort_defaults_to_id(self):
        assert _build_order_by([]) == '"_id" asc'

    def test_column_with_spaces(self):
        assert _build_order_by(['MPN Approval Status asc']) == \
            '"MPN Approval Status" asc'

    def test_multiple_sorts(self):
        assert _build_order_by(['a asc', 'b desc']) == '"a" asc, "b" desc'
