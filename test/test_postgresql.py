# -*- coding: utf-8 -*-

from unittest import TestCase
from unittest.mock import patch
import datetime
from weather_statistic.postgresql import Table


class Cursor:
    @classmethod
    def cursor(cls):
        return cls()

    def _executor(self, request, read: bool=True):
        if not read:
            return request
        else:
            if request == "SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'TestNameTable'":
                return [('id', 'integer'), ('val', 'integer'), ('name', 'character varying')]
            elif request == "SELECT COUNT(*) FROM public.TestNameTable":
                return [(200,)]

    def fetchall(self):
        pass

    def connection_commit(self):
        pass


class TableTest(TestCase):
    @patch("weather_statistic.postgresql.Table._executor", Cursor._executor)
    def setUp(self):
        self.table = Table(cursor=Cursor, table_name='TestNameTable')

    def test__rows_pars(self):
        rows = ([12], [32], [11], [123])
        multi_result = False
        self.assertEqual(12, self.table._rows_pars(rows, multi_result))

        rows = ([12], [32], [11], [123])
        multi_result = True
        self.assertEqual(([12], [32], [11], [123]), self.table._rows_pars(rows, multi_result))

        rows = ([12],)
        multi_result = False
        self.assertEqual(12, self.table._rows_pars(rows, multi_result))

        rows = ([12],)
        multi_result = True
        self.assertEqual([12], self.table._rows_pars(rows, multi_result))

    def test__type_to_sql_injection(self):  # TODO Доделать тесты для datetime
        list_of_type = [1, 132, 'string', 'two string', datetime.datetime, datetime.date, True, False]
        self.assertEqual('1', self.table._type_to_sql_injection(list_of_type[0]))
        self.assertEqual('132', self.table._type_to_sql_injection(list_of_type[1]))
        self.assertEqual("'string'", self.table._type_to_sql_injection(list_of_type[2]))
        self.assertEqual("'two string'", self.table._type_to_sql_injection(list_of_type[3]))
        self.assertEqual('True', self.table._type_to_sql_injection(list_of_type[6]))
        self.assertEqual('False', self.table._type_to_sql_injection(list_of_type[7]))

    @patch("weather_statistic.postgresql.Table._executor", Cursor._executor)
    def test_get_count_of_records(self):
        self.assertEqual(200, self.table.get_count_of_records())