# -*- coding: utf-8 -*-

from unittest import TestCase
import datetime
from weather_statistic import postgresql


class TableTest1(TestCase):
    def setUp(self):
        self.table = postgresql.Table

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
        self.assertEqual('string', self.table._type_to_sql_injection(list_of_type[2]))
        self.assertEqual('two string', self.table._type_to_sql_injection(list_of_type[3]))
        self.assertEqual('True', self.table._type_to_sql_injection(list_of_type[6]))
        self.assertEqual('False', self.table._type_to_sql_injection(list_of_type[7]))
