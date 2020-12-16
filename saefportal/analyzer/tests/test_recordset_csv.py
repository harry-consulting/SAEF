import csv
import json
import os
import datetime
from unittest import TestCase

from django.test import tag

from analyzer.recordset.recordset_csv import RecordsetCSV


@tag("csv")
class RecordsetCSVTests(TestCase):
    def setUp(self):
        CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
        file_name = CURRENT_DIR + '/recordset_csv_test.csv'
        with open(file_name, 'w', newline='') as f:
            field_names = ['t_id', 't_name', 't_value', 't_description', 't_createtime']
            writer = csv.DictWriter(f, delimiter=',', quotechar='"', fieldnames=field_names)
            writer.writeheader()
            writer.writerow({
                't_id': 1,
                't_name': 'test1',
                't_value': 1234.3,
                't_description': 'test 1 description',
                't_createtime': str(datetime.datetime.now())
            })
            writer.writerow({
                't_id': 2,
                't_name': 'test2',
                't_value': 2345.6,
                't_description': 'test 2 description',
                't_createtime': str(datetime.datetime.now())
            })
            writer.writerow({
                't_id': 3,
                't_name': 'test3',
                't_value': 4321.54,
                't_description': 'test 3 description',
                't_createtime': str(datetime.datetime.now())
            })
            writer.writerow({
                't_id': 4,
                't_name': 'test4',
                't_value': 213,
                't_description': 'test 4 description',
                't_createtime': str(datetime.datetime.now())
            })
            writer.writerow({
                't_id': 5,
                't_name': 'test5',
                't_value': 1192,
                't_description': 'test 5 description',
                't_createtime': str(datetime.datetime.now())
            })
            writer.writerow({
                't_id': 6,
                't_name': 'test6',
                't_value': 987,
                't_description': 'test 6 description',
                't_createtime': str(datetime.datetime.now())
            })
        connection_detail = {"file": file_name, "header": True, "delimiter": ","}
        self._recordset_csv = RecordsetCSV(json.dumps(connection_detail))

    def test_get_column_names(self):
        columns_list = ['t_id', 't_name', 't_value', 't_description', 't_createtime']
        self.assertCountEqual(columns_list, self._recordset_csv.get_column_names())

    def test_get_row_count(self):
        self.assertEqual(self._recordset_csv.get_row_count(), 6)

    def test_get_column_count(self):
        self.assertEqual(self._recordset_csv.get_column_count(), 5)

    def test_get_column_type(self):
        self.assertEqual(self._recordset_csv.get_column_type('t_id'), 'int')
        self.assertEqual(self._recordset_csv.get_column_type('t_name'), 'string')
        self.assertEqual(self._recordset_csv.get_column_type('t_value'), 'double')
        self.assertEqual(self._recordset_csv.get_column_type('t_createtime'), 'timestamp')

    def test_get_column_distinct(self):
        list_values = ['test1', 'test2', 'test3', 'test4', 'test5', 'test6']
        self.assertCountEqual(list_values, self._recordset_csv.get_column_distinct('t_name'))

    def test_get_column_min(self):
        self.assertEqual(self._recordset_csv.get_column_min('t_id'), 1)
        self.assertEqual(self._recordset_csv.get_column_min('t_name'), 'test1')
        self.assertEqual(self._recordset_csv.get_column_min('t_value'), 213)

    def test_get_column_max(self):
        self.assertEqual(self._recordset_csv.get_column_max('t_id'), 6)
        self.assertEqual(self._recordset_csv.get_column_max('t_name'), 'test6')
        self.assertEqual(self._recordset_csv.get_column_max('t_value'), 4321.54)