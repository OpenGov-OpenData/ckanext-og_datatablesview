import pytest

import ckanext.og_datatablesview.utils as utils


class TestUtils:

    def test_clean_None_values(self):
        records = [
            {u'emotion': u'aggresive', u'surname': u'vasilov', u'name': u'den', u'level': u'10 ', u'age': 10,
             u'_id': 1},
            {u'emotion': u'aggresive', u'surname': u'Mage', u'name': u'Ancient', u'level': u'1000', u'age': 1000,
             u'_id': 2},
            {u'emotion': u'fear', u'surname': u'Priest', u'name': u'Dark', u'level': u'999', u'age': 999,
             u'_id': 3},
            {u'emotion': u'silent', u'surname': u'Chosen', u'name': u'Neo', u'level': u'maximum', u'age': 26,
             u'_id': 4},
            {u'emotion': u'aggresive', u'surname': u'character', u'name': None, u'level': u'unrecognize',
             u'age': None, u'_id': 5},
            {u'emotion': u'aggresive', u'surname': u'Doe', u'name': u'John', u'level': u'noobie ', u'age': None,
             u'_id': 6},
            {u'emotion': u'aggresive', u'surname': u'Mr', u'name': u'Anderson', u'level': u'10', u'age': 10,
             u'_id': 7}
        ]

        utils.remove_null_values(records)

        numeric_values = [r['age'] for r in records]
        assert(None not in numeric_values)
