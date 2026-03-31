# encoding: utf-8
import pytest

from ckanext.og_datatables_datefilterview.blueprint import (
    _is_valid_date,
    _normalize_date,
    is_date_range_filter,
    is_date_column
)


class TestIsValidDate:
    """Tests for _is_valid_date function"""

    def test_valid_date_yyyy_mm_dd(self):
        assert _is_valid_date('2024-01-15') == True

    def test_valid_date_mm_dd_yyyy(self):
        assert _is_valid_date('01/15/2024') == True

    def test_valid_date_end_of_year(self):
        assert _is_valid_date('2024-12-31') == True
        assert _is_valid_date('12/31/2024') == True

    def test_valid_date_leap_year(self):
        assert _is_valid_date('2024-02-29') == True
        assert _is_valid_date('02/29/2024') == True

    def test_invalid_date_not_leap_year(self):
        assert _is_valid_date('2023-02-29') == False
        assert _is_valid_date('02/29/2023') == False

    def test_invalid_date_month_too_high(self):
        assert _is_valid_date('2024-13-01') == False
        assert _is_valid_date('13/01/2024') == False

    def test_invalid_date_day_too_high(self):
        assert _is_valid_date('2024-01-32') == False
        assert _is_valid_date('01/32/2024') == False

    def test_invalid_date_format(self):
        assert _is_valid_date('invalid') == False
        assert _is_valid_date('2024/01/15') == False
        assert _is_valid_date('01-15-2024') == False

    def test_invalid_date_empty_string(self):
        assert _is_valid_date('') == False


class TestNormalizeDate:
    """Tests for _normalize_date function"""

    def test_normalize_yyyy_mm_dd(self):
        assert _normalize_date('2024-01-15') == '2024-01-15'

    def test_normalize_mm_dd_yyyy(self):
        assert _normalize_date('01/15/2024') == '2024-01-15'

    def test_normalize_end_of_year(self):
        assert _normalize_date('12/31/2024') == '2024-12-31'
        assert _normalize_date('2024-12-31') == '2024-12-31'

    def test_normalize_leap_year(self):
        assert _normalize_date('02/29/2024') == '2024-02-29'

    def test_normalize_single_digit_month_day(self):
        assert _normalize_date('01/05/2024') == '2024-01-05'

    def test_normalize_invalid_date_returns_original(self):
        assert _normalize_date('invalid') == 'invalid'
        assert _normalize_date('13/32/2024') == '13/32/2024'

    def test_normalize_empty_string(self):
        assert _normalize_date('') == ''


class TestIsDateRangeFilter:
    """Tests for is_date_range_filter function"""

    def test_date_range_with_to_separator_yyyy_mm_dd(self):
        is_range, start, end = is_date_range_filter('2024-01-01 to 2024-12-31')
        assert is_range == True
        assert start == '2024-01-01'
        assert end == '2024-12-31'

    def test_date_range_with_to_separator_mm_dd_yyyy(self):
        is_range, start, end = is_date_range_filter('01/01/2024 to 12/31/2024')
        assert is_range == True
        assert start == '2024-01-01'
        assert end == '2024-12-31'

    def test_date_range_with_to_case_insensitive(self):
        is_range, start, end = is_date_range_filter('01/01/2024 TO 12/31/2024')
        assert is_range == True
        assert start == '2024-01-01'
        assert end == '2024-12-31'

    def test_date_range_with_comma_separator(self):
        is_range, start, end = is_date_range_filter('2024-01-01,2024-12-31')
        assert is_range == True
        assert start == '2024-01-01'
        assert end == '2024-12-31'

    def test_date_range_with_dash_separator(self):
        is_range, start, end = is_date_range_filter('2024-01-01 - 2024-12-31')
        assert is_range == True
        assert start == '2024-01-01'
        assert end == '2024-12-31'

    def test_date_range_normalizes_mm_dd_yyyy(self):
        is_range, start, end = is_date_range_filter('01/15/2024 to 03/20/2024')
        assert is_range == True
        assert start == '2024-01-15'
        assert end == '2024-03-20'

    def test_single_date_not_a_range(self):
        is_range, start, end = is_date_range_filter('2024-01-15')
        assert is_range == False
        assert start is None
        assert end is None

    def test_invalid_date_range(self):
        is_range, start, end = is_date_range_filter('2024-13-01 to 2024-14-31')
        assert is_range == False

    def test_empty_string(self):
        is_range, start, end = is_date_range_filter('')
        assert is_range == False
        assert start is None
        assert end is None

    def test_date_range_with_extra_spaces(self):
        is_range, start, end = is_date_range_filter('  2024-01-01  to  2024-12-31  ')
        assert is_range == True
        assert start == '2024-01-01'
        assert end == '2024-12-31'


class TestIsDateColumn:
    """Tests for is_date_column function"""

    def test_timestamp_column(self):
        fields = [
            {'id': 'created_date', 'type': 'timestamp'},
            {'id': 'name', 'type': 'text'}
        ]
        assert is_date_column('created_date', fields) == True

    def test_timestamptz_column(self):
        fields = [
            {'id': 'modified_at', 'type': 'timestamptz'},
            {'id': 'name', 'type': 'text'}
        ]
        assert is_date_column('modified_at', fields) == True

    def test_date_column(self):
        fields = [
            {'id': 'birth_date', 'type': 'date'},
            {'id': 'name', 'type': 'text'}
        ]
        assert is_date_column('birth_date', fields) == True

    def test_non_date_column(self):
        fields = [
            {'id': 'name', 'type': 'text'},
            {'id': 'age', 'type': 'numeric'}
        ]
        assert is_date_column('name', fields) == False
        assert is_date_column('age', fields) == False

    def test_column_not_in_fields(self):
        fields = [
            {'id': 'name', 'type': 'text'}
        ]
        assert is_date_column('missing_column', fields) == False

    def test_empty_fields(self):
        assert is_date_column('any_column', []) == False

    def test_case_sensitivity(self):
        fields = [
            {'id': 'created_date', 'type': 'TIMESTAMP'}
        ]
        # Type comparison is case-insensitive
        assert is_date_column('created_date', fields) == True


class TestDateFormatIntegration:
    """Integration tests for date format handling"""

    def test_mm_dd_yyyy_converts_to_normalized_range(self):
        # Test that MM/DD/YYYY format is properly validated and normalized
        date_str = '01/15/2024'
        assert _is_valid_date(date_str) == True
        normalized = _normalize_date(date_str)
        assert normalized == '2024-01-15'

    def test_range_with_mixed_valid_formats_same_type(self):
        # Both dates in same format should work
        is_range, start, end = is_date_range_filter('01/01/2024 to 12/31/2024')
        assert is_range == True
        # Both should be normalized
        assert start == '2024-01-01'
        assert end == '2024-12-31'

    def test_yyyy_mm_dd_stays_normalized(self):
        # YYYY-MM-DD format should remain unchanged
        date_str = '2024-01-15'
        assert _is_valid_date(date_str) == True
        normalized = _normalize_date(date_str)
        assert normalized == '2024-01-15'
