# -*- coding: utf-8 -*-

import time
import requests
import re
import datetime
from abc import abstractmethod
from abc import ABC
from bs4 import BeautifulSoup
from weather_statistic.recorder_error import recorder_error
from weather_statistic.constants import (YX_CURR_FEEL,
                                         YX_CURR_HUMIDITY,
                                         YX_CURR_CONDITION,
                                         YX_CURR_TEMP,
                                         YX_CURR_PRESSURE,
                                         YX_CURR_WIND,
                                         YX_10DAYS_TEMP,
                                         YX_10DAYS_FEEL,
                                         YX_10DAYS_CONDITION,
                                         YX_10DAYS_HUMIDITY,
                                         YX_10DAYS_PRESSURE,
                                         YX_10DAYS_WIND,
                                         URLS_YANDEX)


@recorder_error
class Page:
    """Класс описывающий страницу.

    :param url: URL адрес страницы.

    :param timeout: таймаут для запроса на страницу.

    """
    def __init__(self, url, timeout=20):
        self._url = url
        self._timeout = timeout
        self.html_data, self.html_status_code, self.html_ok = self.get_html(self._url, self._timeout)
        self.page_bs4 = BeautifulSoup(self.html_data, 'lxml') if self.html_ok else None

    @staticmethod
    @recorder_error
    def get_html(url, timeout):
        """Метод для получения html кода страницы.

        :param url: URL адрес страницы.

        :param timeout: таймаут для запроса на страницу.

        """
        try:
            data = requests.get(url, timeout=timeout)
            return data.text, data.status_code, data.ok
        except requests.ConnectionError as err:
            return None, 1404, False


class SearcherInPage(ABC):
    """Класс описывающий информацию по одному виду погоды

    :param page_bs4: Данные HTML страницы для парсинга информации, тип BeautifulSoup

    :param setup_pattern: Путь до желаемого параметра

    """
    @recorder_error
    def __init__(self, page_bs4: BeautifulSoup, setup_pattern):
        self.setup_pattern = self.pattern_format(setup_pattern)
        self.weather_data_bs4 = self.data_extractor(page_bs4, self.setup_pattern)
        self.weather_data = self._spreader(self.weather_data_bs4)

    @staticmethod
    @recorder_error
    def pattern_format(setup_patterns):
        """Метод для форматирования пути в требуемый формат.
        Метод раскладываем строку пути в список и формирует подсписки в виде словарей, где
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

    @recorder_error
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

    @recorder_error
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
    @recorder_error
    def __init__(self, page_bs4: BeautifulSoup, setup_pattern):
        super(YxWeatherData, self).__init__(page_bs4, setup_pattern)

    @recorder_error
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

        @recorder_error
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

        @recorder_error
        def format_from_garbage(data):
            """Метод для отсечеия лишних символов - точки, градусы, проценты и т.д"""
            out = list()
            if isinstance(data, (list, tuple)):
                for data_i in data:
                    if isinstance(data_i, (list, tuple)):
                        out.append(format_from_garbage(data_i) if len(data_i) > 1
                                   else format_from_garbage(data_i[0]))
                    else:
                        out.append(re.findall(r"[а-яА-Я\s]+|-\d{1,3}|\d+", data_i))
                return out
            else:
                return re.findall(r"[а-яА-Я\s]+|-\d{1,3}|\d+", data)
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
    @recorder_error
    def __init__(self, urls: dict):
        self.urls = urls
        self.current, self.calendar = self._get_data(self.urls)

    @recorder_error
    def _get_data(self, urls):
        self.page_current = Page(urls['current'])
        self.page_calendar = Page(urls['calendar'])
        self.date_time_update = datetime.datetime.today().utcnow()
        struct_current, struct_calendar = dict(), dict()
        struct_current['temperature'] = YxWeatherData(self.page_current.page_bs4, YX_CURR_TEMP).weather_data
        struct_current['feel'] = YxWeatherData(self.page_current.page_bs4, YX_CURR_FEEL).weather_data
        struct_current['humidity'] = YxWeatherData(self.page_current.page_bs4, YX_CURR_HUMIDITY).weather_data
        struct_current['condition'] = YxWeatherData(self.page_current.page_bs4, YX_CURR_CONDITION).weather_data
        struct_current['pressure'] = YxWeatherData(self.page_current.page_bs4, YX_CURR_PRESSURE).weather_data
        struct_calendar['temperature'] = YxWeatherData(self.page_calendar.page_bs4, YX_10DAYS_TEMP).weather_data
        struct_calendar['feel'] = YxWeatherData(self.page_calendar.page_bs4, YX_10DAYS_FEEL).weather_data
        struct_calendar['humidity'] = YxWeatherData(self.page_calendar.page_bs4, YX_10DAYS_HUMIDITY).weather_data
        struct_calendar['condition'] = YxWeatherData(self.page_calendar.page_bs4, YX_10DAYS_CONDITION).weather_data
        struct_calendar['pressure'] = YxWeatherData(self.page_calendar.page_bs4, YX_10DAYS_PRESSURE).weather_data
        return struct_current, struct_calendar

    @recorder_error
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
    @recorder_error
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
