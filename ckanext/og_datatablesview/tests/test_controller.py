from ckanext.og_datatablesview.controller import DataTablesController
from nose.tools import assert_false


class TestController:

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

        fields = [
            {u'type': 'int', u'id': '_id'},
            {u'info': {u'notes': u'', u'type_override': u'', u'label': u''}, u'type': u'text', u'id': u'name'},
            {u'info': {u'notes': u'', u'type_override': u'', u'label': u''}, u'type': u'text', u'id': u'surname'},
            {u'info': {u'notes': u'', u'type_override': u'', u'label': u''}, u'type': u'text', u'id': u'emotion'},
            {u'info': {u'notes': u'', u'type_override': u'numeric', u'label': u''}, u'type': u'numeric',
             u'id': u'age'},
            {u'info': {u'notes': u'', u'type_override': u'', u'label': u''}, u'type': u'text', u'id': u'level'}
        ]

        DataTablesController.remove_None_values_from_numeric_fields(records, fields)

        numeric_values = [r['age'] for r in records]
        assert_false(None in numeric_values)
