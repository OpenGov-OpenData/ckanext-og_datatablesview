import pytest

import ckanext.og_datatablesview.utils as utils


class TestUtils:

    def test_clean_None_values(self):
        records = [
            {"name": "Sunita", "age": 51},
            {"name": "Bowan", "age": 68},
            {"name": "Adam", "age": None}
        ]

        utils.remove_null_values(records)

        numeric_values = [r['age'] for r in records]
        assert(None not in numeric_values)
