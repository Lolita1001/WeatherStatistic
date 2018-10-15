# -*- coding: utf-8 -*-

import datetime
from weather_statistic.recorder_error import recorder_error

class Table:  # TODO Добавить обработку исключений
    """Класс таблица. Позволяет взаимодействовать с таблицей SQL"""
    def __init__(self, cursor, table_name: str):
        self._cursor = cursor
        self._table_name = table_name
        self._get_structure_of_table()
        #
        # Structure of record -- dict:
        # {temp: (2, 5), condition: 'sun', pressure: 79, wind: (6.9, 'west'), feeling_temp: 6}
        #
        self.last_day_mor = None
        self.last_day_day = None
        self.last_day_evn = None
        self.last_day_ngh = None

    def get_count_of_records(self):
        """Метод получения колличества записей в таблице"""
        return self.select(specific='COUNT(*)')

    def _get_structure_of_table(self):
        """Метод получения структуры таблицы"""

        request = f"SELECT column_name, data_type FROM information_schema.columns WHERE table_name = " \
                  f"'{self._table_name}'"
        results = self.select(user_request=request, multi_result=True)
        self._is_created = results is not None
        self._structure = results

    def _executor(self, request: str, read: bool=True):
        """Метод для выполнения запросов на чтение и запись.

        :param request: запрос.

        :param read: True определяет запрос на чтение (по умолчанию), False на запись.

        """
        self._cursor.execute(request)
        if read:
            return self._cursor.fetchall()
        else:
            self._cursor.connection.commit()
            return True

    def select(self, specific: str=None, condition: str=None, user_request: str=None, multi_result: bool=False):
        """Метод запроса "Select" из базы данных.

        :param user_request: определяет пользовательский запрос, шаблон не используется.

        :param specific: определяет столбцы для запроса.

        :param condition: дополнительное условие.

        :param multi_result: определяет вид return значения, False одно значение(по умолчанию), True множественный.

        По умолчанию выполняет запрос шаблонного вида:

        SELECT {spec} FROM public.{self._table_name}{cond}

        """
        spec = '*' if specific is None else specific
        cond = '' if condition is None else f' WHERE {condition}'
        _request = f"SELECT {spec} FROM public.{self._table_name}{cond}" if user_request is None else user_request
        rows: tuple = self._executor(request=_request)
        return self._rows_pars(rows=rows, multi_result=multi_result)

    @staticmethod
    def _rows_pars(rows, multi_result):
        """Статическая функция для парсинга полученных данных из DB

        :param rows: данные.

        :param multi_result: определяет вид return значения, False одно значение(по умолчанию), True множественный.

        """
        if rows:
            if not multi_result:
                for row in rows:
                    for i in row:
                        return i  # вывод первого вхождения из кортежа и списка
            else:  # если множественный вывод
                if len(rows) == 1:  # если кортеж из одного элемента
                    return rows[0]  # избавляемся от кортежа и выводим список
                else:  # если кортеж из нескольких элементов
                    return rows  # выводим весь кортеж
        else:
            return None  # если данных не получили, выводим None

    @staticmethod
    def _type_to_sql_injection(variable) -> str:  # TODO добавить с плавующей точкой. Незабыть обновить тест
        """В зависимости от типа переменной форматирует для SQL иньекции"""
        if isinstance(variable, (int, bool)):
            return '%s' % variable
        elif isinstance(variable, str):
            return "\'%s\'" % variable
        elif isinstance(variable, datetime.datetime):
            return '%s' % variable.strftime("TIMESTAMP\'%Y-%m-%d %H:%M:%S\'")
        elif isinstance(variable, datetime.date):
            return '%s' % variable.strftime("DATE\'%Y-%m-%d\'")

    def create(self, *name_columns, user_request: str=None):
        """Метод для создания таблицы. Таблица может быть создана только в случае если она не была создана ранее

        :param name_columns: названия и тип данных колонок.

        :param user_request: определяет пользовательский запрос, шаблон не используется.

        Шаблон по умолчанию:

        CREATE TABLE IF NOT EXISTS public.{self._table_name} (*name_columns)

        """
        if not self._is_created:
            request = f"CREATE TABLE IF NOT EXISTS public.{self._table_name} ("
            for num, i in enumerate(name_columns, start=1):
                request += f'{i}'
                if num != name_columns.__len__():
                    request += ', '
            request += ")"
            request = request if user_request is None else user_request
            results = self._executor(request=request, read=False)
            self._get_structure_of_table()
            return results
        else:
            return False

    def alter(self, action: str, user_request: str=None):
        """Метод для внесения изменений в существующую таблицу

        :param action: изменение в таблице.

        :param user_request: определяет пользовательский запрос, шаблон не используется.

        Шаблон по умолчанию:

        ALTER TABLE {self._table_name} {action}

        """
        request = f"ALTER TABLE {self._table_name} {action}" if user_request is None else user_request
        self._executor(request=request, read=False)

    def insert(self, *args, user_request: str=None, **kwargs):  # TODO сделать проверку на наличии колонки из _structure
        """Меток для внесения значений в таблицу

        :param args: значения для внесения в таблицу (последовательно по колонкам).

        :param kwargs: наименование колонки и значение для внесения в таблицу.

        :param user_request: определяет пользовательский запрос, шаблон не используется.

        Шаблон по умолчанию:

        names_columns и value_columns полачаются из **kwags

        INSERT INTO {self._table_name} ({names_columns}) VALUES ({value_columns})

        """
        request = ''
        if user_request:
            request = user_request
        elif kwargs:
            names_columns = ''
            value_columns = ''
            for item_kwargs, key_kwargs in enumerate(kwargs.keys(), start=1):
                names_columns += key_kwargs
                value_columns += self._type_to_sql_injection(kwargs[key_kwargs])
                if item_kwargs != kwargs.__len__():
                    names_columns += ', '
                    value_columns += ', '
            request = f"INSERT INTO {self._table_name} ({names_columns}) VALUES ({value_columns})"
        elif args:
            for seq_args, item_args in enumerate(args, start=1):
                if type(item_args) is list:
                    for seq_list, item_list in enumerate(item_args, start=1):
                        request += self._type_to_sql_injection(item_list)
                        request += ', ' if seq_list != item_args.__len__() else ""
                else:
                    request += self._type_to_sql_injection(item_args)
                    request += ', ' if seq_args != args.__len__() else ""
            request = f"INSERT INTO {self._table_name} VALUES ({request})"
        else:
            return
        self._executor(request=request, read=False)
