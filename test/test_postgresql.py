# -*- coding: utf-8 -*-

from unittest import TestCase
from weather_statistic import postgresql


class TableTest1(TestCase):
    def setUp(self):
        self.table = postgresql.Table

    def test_rows_pars(self):
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
