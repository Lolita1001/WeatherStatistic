# -*- coding: utf-8 -*-

import time
import requests
import inspect
from bs4 import BeautifulSoup
from weather_statistic.constants import (YX_CURR_FEEL,
                                         YX_CURR_HUMIDITY,
                                         YX_CURR_CONDITION,
                                         YX_CURR_TEMP,
                                         YX_10DAYS_TEMP,
                                         YX_10DAYS_FEEL,
                                         YX_10DAYS_CONDITION,
                                         YX_10DAYS_HUMIDITY,
                                         YX_10DAYS_PRESSURE,
                                         YX_10DAYS_WIND)


class Page:
    """Класс описывающий страницу.

    :param url: URL адрес страницы.

    :param timeout: таймаут для запроса на страницу.

    """
    def __init__(self, url, timeout=20):
        self._url = url
        self._timeout = timeout
        self.html_data, self.html_status_code, self.html_ok = self.get_html(self._url, self._timeout)
        self.data_bs4 = BeautifulSoup(self.html_data, 'lxml') if self.html_ok else None

    @staticmethod
    def get_html(url, timeout):
        """Метод для получения html кода страницы.

        :param url: URL адрес страницы.

        :param timeout: таймаут для запроса на страницу.

        """
        try:
            data = requests.get(url, timeout=timeout)
            return data.text, data.status_code, data.ok
        except requests.ConnectionError as err:
            print(err)
            return None, 1404, False


class OneWeatherInfo:
    """Класс описывающий информацию по одному виду погоды

    :param data_bs4: Данные HTML страницы для парсинга информации, тип BeautifulSoup

    :param setup_pattern: Путь до желаемого параметра

    """
    def __init__(self, data_bs4: BeautifulSoup, setup_pattern):
        self._setup_pattern = self.pattern_format(setup_pattern)
        self._data_bs4 = data_bs4
        self.info = self.data_extractor(self._data_bs4, self._setup_pattern)

    @staticmethod
    def pattern_format(setup_pattern):
        """Метод для форматирования пути в требуемый формат.
        Метод раскладываем строку пути в список и формирует подсписки в виде словарей, где
        ключ и значения это именованные аргументы для BS4

        Пример:

        'body > div.b-page__container > div.content

        [[body, {'':''}], ['div', {'class_':'page__container'}], ['div', {'class_':'content'}]]

        """
        setup_pattern = setup_pattern.split(' > ')
        out_pattern = []
        for pattern_path in setup_pattern:
            pattern_path = pattern_path.split('.')  # Разделяю шаблон для подстановки в аттрибуты
            if len(pattern_path) > 1:
                temp_search_path = pattern_path[1]
                pattern_path.pop()
                pattern_path.append({'class_': temp_search_path})
            else:
                pattern_path.append({'': ''})
            out_pattern.append(pattern_path)
        return out_pattern

    def data_extractor(self, data_bs4, setup_pattern):
        """Метод для извлечения данных из data_bs4"""
        data = [data_bs4]
        try:
            for search_path in setup_pattern:  # Итерация по каждому шаблону поиска
                data = data[0].find_all(search_path[0], **search_path[1])  # поиск по шаблону и перезапись
        except BaseException as f:  # TODO обработать исключение как положенно
            print(data)
            print(f)
            return None
        assert len(data) == 1, 'Кол-во результатов больше 1'
        return data

    def info_text(self):
        info_text = []
        for enum, i in enumerate(self.info):
            info_text.append(self.info[enum].text)
        return info_text


class FewWeatherInfo(OneWeatherInfo):
    """Класс описывающий множественную информацию по одному виду погоды"""
    def __init__(self, data_bs4, setup_pattern):
        self._setup_pattern_second = self.pattern_format(setup_pattern[1])
        super().__init__(data_bs4, setup_pattern[0])

    def data_extractor(self, data_bs4, setup_pattern):
        """Метод для извлечения данных из data_bs4"""
        data = [data_bs4]
        data1 = [[data_bs4]]
        try:
            for search_path in setup_pattern:  # Итерация по каждому шаблону поиска
                for y in range(len(data1)):
                    data1 = [data1[y][x].find_all(search_path[0], **search_path[1]) for x in range(len(data1[y]))]
                    data1 = [x for x in data1 if x != []]
                data = data[0].find_all(search_path[0], **search_path[1])  # поиск по шаблону и перезапись
        except BaseException as f:  # TODO обработать исключение как положенно
            print(data.source)
            print(f)
            return None
        if inspect.stack()[1][3] != '__init__':  # Проверка на имя вызвавшего метода
            return data1
        else:
            return self.data_splitter(data1[0])

    def data_splitter(self, data_bs4):
        """Метод для итерированию по нескольким результатам"""
        data = []
        for day in data_bs4:
            data.append(self.data_extractor(day, self._setup_pattern_second))
        return data

    def info_text(self):
        info_text = []
        for enumi, i in enumerate(self.info):
            for enumj, j in enumerate(i):
                info_text.append(self.info[enumi][enumj][0].text)
        return info_text


class YxWeather:
    def __init__(self, urls: dict):
        temp1 = time.time()
        self.page_current = Page(urls['current'])
        self.page_calendar = Page(urls['calendar'])
        self.current_temperature = OneWeatherInfo(self.page_current.data_bs4, YX_CURR_TEMP)
        self.current_temperature_feel = OneWeatherInfo(self.page_current.data_bs4, YX_CURR_FEEL)
        self.current_humidity = OneWeatherInfo(self.page_current.data_bs4, YX_CURR_HUMIDITY)
        self.current_condition = OneWeatherInfo(self.page_current.data_bs4, YX_CURR_CONDITION)
        self.calendar_temperature = self._expanded_calendar(
            FewWeatherInfo(self.page_calendar.data_bs4, YX_10DAYS_TEMP).info)
        self.calendar_temperature_feel = self._expanded_calendar(
            FewWeatherInfo(self.page_calendar.data_bs4, YX_10DAYS_FEEL).info)
        self.calendar_temperature_humidity = self._expanded_calendar(
            FewWeatherInfo(self.page_calendar.data_bs4, YX_10DAYS_HUMIDITY).info)
        self.calendar_temperature_condition = self._expanded_calendar(
            FewWeatherInfo(self.page_calendar.data_bs4, YX_10DAYS_CONDITION).info)
        self.calendar_temperature_pressure = self._expanded_calendar(
            FewWeatherInfo(self.page_calendar.data_bs4, YX_10DAYS_PRESSURE).info)
        self.calendar_temperature_wind = self._expanded_calendar(
            FewWeatherInfo(self.page_calendar.data_bs4, YX_10DAYS_WIND).info)
        print(time.time() - temp1)

    def _expanded_calendar(self, data):
        out = list()
        for i in self._expander_iterator(data):
            out.append(i)
        return out

    @staticmethod
    def _expander_iterator(data):
        for day in data:
            out = list()
            for result_set in day:
                for tag in result_set:
                    out.append(tag.text)
            yield out
