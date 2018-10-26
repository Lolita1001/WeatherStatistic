# -*- coding: utf-8 -*-

import time
import requests
import re
import datetime
import pickle
from abc import abstractmethod
from abc import ABC
from bs4 import BeautifulSoup
from weather_statistic.recorder_error import recorder_error
from weather_statistic.constants import (YX_CURR,
                                         YX_CALENDAR,
                                         YX_TEMPLATE,
                                         HEADERS_REQ)


class Page:
    """Класс описывающий страницу.

    :param url: URL адрес страницы.

    :param timeout: таймаут для запроса на страницу.

    :param debug_read_file: файл для чтения из файла и замены результата request

    :param debug_write_file: файл для записи в файл результата request

    :param find_template: шаблон для первичного поиска в полученном HTML коде

    """
    def __init__(self, url, timeout=20, debug_read_file=None, debug_write_file=None, find_template=None):
        self._url = url
        self._timeout = timeout
        if debug_read_file:
            with open(debug_read_file, 'rb') as f:
                data = pickle.load(f)
                self.html_data, self.html_status_code, self.html_ok = data['html_data'], data['html_status_code'], \
                                                                      data['html_ok']
        else:
            self.html_data, self.html_status_code, self.html_ok = self.get_html(self._url, self._timeout)
        if debug_write_file:
            with open(debug_write_file, 'wb') as f:
                data = {'html_data': self.html_data, 'html_status_code': self.html_status_code, 'html_ok': self.html_ok}
                pickle.dump(data, f)
        if find_template is None:
            self.page_bs4 = BeautifulSoup(self.html_data, 'lxml') if self.html_ok else None
        else:
            self.page_bs4 = BeautifulSoup(self.html_data, 'lxml'). \
                find(find_template[0], **find_template[1]) if self.html_ok else None

    @staticmethod
    def get_html(url, timeout):
        """Метод для получения html кода страницы.

        :param url: URL адрес страницы.

        :param timeout: таймаут для запроса на страницу.

        """
        try:
            data = requests.get(url, headers=HEADERS_REQ, timeout=timeout)
            return data.text, data.status_code, data.ok
        except requests.ConnectionError as err:
            return None, 1404, False


class SearcherInPage(ABC):
    """Класс описывающий информацию по одному виду погоды

    :param page_bs4: Данные HTML страницы для парсинга информации, тип BeautifulSoup

    :param setup_pattern: Путь до желаемого параметра

    """

    def __init__(self, page_bs4: BeautifulSoup, setup_pattern):
        self.setup_pattern = self.pattern_format(setup_pattern)
        self.weather_data_bs4 = self.data_extractor(page_bs4, self.setup_pattern)
        self.weather_data = self._spreader(self.weather_data_bs4)

    @staticmethod
    def pattern_format(setup_patterns):
        """Метод для форматирования пути в требуемый формат.
        Метод раскладывает строку пути в список и формирует подсписки в виде словарей, где
        ключ и значения это именованные аргументы для BS4

        Пример:

        'body > div.b-page__container > div.content

        [[body, {'':''}], ['div', {'class_':'page__container'}], ['div', {'class_':'content'}]]

        """
        if not isinstance(setup_patterns, (str, list)):
            assert TypeError, 'Шаблон поиска должен быть типа строка или список'
        setup_patterns = [setup_patterns] if isinstance(setup_patterns, str) else setup_patterns
        out_pattern = list()
        for pattern in setup_patterns:
            pattern = pattern.split(' > ')
            out_pattern_path = list()
            for pattern_path in pattern:
                pattern_path = pattern_path.split('.')  # Разделяю шаблон для подстановки в аттрибуты
                if len(pattern_path) > 1:
                    temp_search_path = pattern_path[1]
                    pattern_path.pop()
                    pattern_path.append({'class_': temp_search_path})
                else:
                    pattern_path.append({'': ''})
                out_pattern_path.append(pattern_path)
            out_pattern.append(out_pattern_path)
        return out_pattern

    def data_extractor(self, page_bs4, setup_pattern):
        """Метод для извлечения данных из page_bs4"""
        data = [[page_bs4]]
        try:
            for search_path in setup_pattern[0]:  # Итерация по каждому шаблону поиска
                for y in range(len(data)):
                    data = [data[y][x].find_all(search_path[0], **search_path[1]) for x in range(len(data[y]))]
                    data = [x for x in data if x != []] if len(data) > 1 else data
        except BaseException as f:  # TODO обработать исключение как положенно
            print(f)
            return None
        if len(setup_pattern) == 1:  # Проверка на имя вызвавшего метода
            return data
        else:
            return self._data_splitter(data[0], [setup_pattern[1]])

    def _data_splitter(self, data_bs4, setup_pattern):
        """Метод для итерированию по нескольким результатам"""
        data = list()
        for day in data_bs4:
            data.append(self.data_extractor(day, setup_pattern))
        return data

    @abstractmethod
    def _spreader(self, weather_data_bs4) -> any:
        """Метод для разложения данных по структуре
        Выполнен как абстрактный метод и должен быть разработан для каждого сайта индивидуально"""
        pass


class YxWeatherData(SearcherInPage):
    def __init__(self, page_bs4: BeautifulSoup, setup_pattern):
        super(YxWeatherData, self).__init__(page_bs4, setup_pattern)

    def _spreader(self, weather_data_bs4):
        def info_text(data):
            """Метод из данных BS4 плучает текстовые значения"""
            text = list()
            if isinstance(data, (list, tuple, BeautifulSoup)):
                for data_i in data:
                    if isinstance(data_i, (list, tuple, BeautifulSoup)):
                        text.append(info_text(data_i))
                    else:
                        text.append(data_i.text)
                return text
            else:
                return data.text

        def list_of_one_element_expand(data):
            """Метод для свертывания избыточных списков (список содержищий только одно значени)"""
            run = True
            out = list()
            while run:
                out = list()
                run = False
                if isinstance(data, list):
                    for data_i in data:
                        if isinstance(data_i, list) and len(data_i) > 1:
                            out.append(list_of_one_element_expand(data_i))
                        elif isinstance(data_i, list) and len(data_i) == 1:
                            out.append(data_i[0])
                            run = True
                        else:
                            out.append(data_i)
                    data = out
                else:
                    out = data
            return out

        def format_from_garbage(data):
            """Метод для отсечеия лишних символов - точки, градусы, проценты и т.д"""
            pattern = r"[а-яА-Я]{4,}[ ]?[а-яА-Я]{4,}|[а-яА-Я]{4,}|[+-]?[0-9]*[,]?[0-9]+"
            out = list()
            if isinstance(data, (list, tuple)):
                for data_i in data:
                    if isinstance(data_i, (list, tuple)):
                        out.append(format_from_garbage(data_i) if len(data_i) > 1
                                   else format_from_garbage(data_i[0]))
                    else:
                        out.append(re.findall(pattern, data_i))
                return out
            else:
                return re.findall(pattern, data)

        return list_of_one_element_expand(format_from_garbage(info_text(weather_data_bs4)))


class YxWeather:
    """Класс описывает погоду с сайта Yx.

    :param urls: URL адреса в виде словаря, где ключ 'current' содержит адрес текущей погоды, ключ 'calendar' адрес
    прогноза погоды на 10 дней.

    Данные о погоде представляют структуру:

        current/calendar = {'temperature' : None,
                            'feel' : None,
                            'humidity' : None,
                            'condition' : None,
                            'pressure' : None}

    """

    def __init__(self, urls: dict):
        self.urls = urls
        self.current, self.calendar = self._get_data(self.urls)

    def _get_data(self, urls):
        self.page_current = Page(urls['current'], debug_read_file='request_current.txt',
                                 find_template=YX_TEMPLATE['current'])
        # time.sleep(3)
        self.page_calendar = Page(urls['calendar'], debug_read_file='request_calendar.txt',
                                  find_template=YX_TEMPLATE['calendar'])
        self.date_time_update = datetime.datetime.today().utcnow()
        '''
        struct_current, struct_calendar = dict(), dict()
        struct_current['temperature'] = YxWeatherData(self.page_current.page_bs4, YX_CURR_TEMP).weather_data
        struct_current['feel'] = YxWeatherData(self.page_current.page_bs4, YX_CURR_FEEL).weather_data
        struct_current['humidity'] = YxWeatherData(self.page_current.page_bs4, YX_CURR_HUMIDITY).weather_data
        struct_current['condition'] = YxWeatherData(self.page_current.page_bs4, YX_CURR_CONDITION).weather_data
        struct_current['pressure'] = YxWeatherData(self.page_current.page_bs4, YX_CURR_PRESSURE).weather_data[0]
        struct_calendar['temperature'] = YxWeatherData(self.page_calendar.page_bs4, YX_10DAYS_TEMP).weather_data
        struct_calendar['feel'] = YxWeatherData(self.page_calendar.page_bs4, YX_10DAYS_FEEL).weather_data
        struct_calendar['humidity'] = YxWeatherData(self.page_calendar.page_bs4, YX_10DAYS_HUMIDITY).weather_data
        struct_calendar['condition'] = YxWeatherData(self.page_calendar.page_bs4, YX_10DAYS_CONDITION).weather_data
        struct_calendar['pressure'] = YxWeatherData(self.page_calendar.page_bs4, YX_10DAYS_PRESSURE).weather_data'''
        struct_current = {key: YxWeatherData(self.page_current.page_bs4, YX_CURR[key]).weather_data for key in YX_CURR}
        struct_calendar = {key: YxWeatherData(self.page_calendar.page_bs4, YX_CALENDAR[key]).weather_data for key in
                           YX_CALENDAR}
        # FIXME ---BEGIN--- Поиск решения в выборе оптимальной структуры данных для погоды
        test_out = list(zip(*struct_calendar.values()))
        weak = dict()
        for num, day in enumerate(test_out):
            mor, day, eve, night = zip(*day)

            def set_data(data):
                out = WeatherStructure()
                out.set_weather(data[0], data[1], data[2], data[3], data[4], data[5])
                return out

            # testlist = list(map(set_data, [mor, day, eve, night]))
            testlist = dict(zip(['morning', 'day', 'evening', 'night'], (map(set_data, [mor, day, eve, night]))))
            weak[(datetime.datetime.today().now() + datetime.timedelta(days=num)).strftime('%d%m%y')] = testlist
        # FIXME ---END---
        return struct_current, struct_calendar

    def update_and_get_different(self):
        """Метод для обновления и получаения изменений в текущей/прогнозе погоды

        :return два (current и calendar) словаря с изменениями

        """
        current_new, calendar_new = self._get_data(self.urls)
        curr_diff = DictDiffer(current_new, self.current).changed()
        calendar_diff = DictDiffer(calendar_new, self.calendar).changed()
        curr_for_sql = {x: current_new[x] for x in curr_diff}
        calendar_for_sql = {x: calendar_new[x] for x in calendar_diff}
        self.current, self.calendar = current_new, calendar_new
        return curr_for_sql, calendar_for_sql


class DictDiffer(object):
    """
    Calculate the difference between two dictionaries as:
    (1) items added
    (2) items removed
    (3) keys same in both but changed values
    (4) keys same in both and unchanged values
    """

    def __init__(self, current_dict, past_dict):
        self.current_dict, self.past_dict = current_dict, past_dict
        self.set_current, self.set_past = set(current_dict.keys()), set(past_dict.keys())
        self.intersect = self.set_current.intersection(self.set_past)

    def added(self):
        return self.set_current - self.intersect

    def removed(self):
        return self.set_past - self.intersect

    def changed(self):
        return set(o for o in self.intersect if self.past_dict[o] != self.current_dict[o])

    def unchanged(self):
        return set(o for o in self.intersect if self.past_dict[o] == self.current_dict[o])


class WeatherStructure:
    def __init__(self):
        self.timestamp = None
        self.weather = dict()
        self.weather['temperature'] = None
        self.weather['feel'] = None
        self.weather['condition'] = None
        self.weather['humidity'] = None
        self.weather['pressure'] = None
        self.weather['wind'] = None

    def set_weather(self, temperature, feel, condition, humidity, pressure, wind, day_offset=0):
        if not isinstance(temperature, list):
            temperature = [temperature, temperature]
        self.timestamp = datetime.datetime.today().now() + datetime.timedelta(days=day_offset)
        self.weather['temperature'] = temperature
        self.weather['feel'] = feel
        self.weather['condition'] = condition
        self.weather['humidity'] = humidity
        self.weather['pressure'] = pressure
        self.weather['wind'] = wind
