# -*- coding: utf-8 -*-

URLS_YX = {'current': 'https://yandex.ru/pogoda/samara/?from=home',
           'calendar': 'https://yandex.ru/pogoda/samara/details?'}

HEROKU_RUN = 'HEROKU_RUN'
HEADERS_REQ = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                             'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36'}
YX_CURR, YX_CALENDAR, YX_TEMPLATE = dict(), dict(), dict()
YX_CURR['temperature'] = 'div.fact__temp-wrap > a.link fact__basic day-anchor i-bem > div > span.temp__value'
YX_CURR['feel'] = 'div.fact__temp-wrap > dl.term term_orient_h fact__feels-like > dd > div > span.temp__value'
YX_CURR['condition'] = 'div.fact__temp-wrap > div.fact__condition day-anchor i-bem'
YX_CURR['humidity'] = 'div.fact__props > dl.term term_orient_v fact__humidity > dd'
YX_CURR['pressure'] = 'div.fact__props > dl.term term_orient_v fact__pressure > dd'
YX_CURR['wind'] = 'div.fact__props > dl.term term_orient_v fact__wind-speed > dd'

YX_CALENDAR['temperature'] = ['table.weather-table', 'tbody > td.weather-table__body-cell > div.weather-table__temp']
YX_CALENDAR['feel'] = ['table.weather-table',
                       'tbody > td.weather-table__body-cell weather-table__body-cell_type_feels-like']
YX_CALENDAR['condition'] = ['table.weather-table',
                            'tbody > td.weather-table__body-cell weather-table__body-cell_type_condition']
YX_CALENDAR['humidity'] = ['table.weather-table',
                           'tbody > td.weather-table__body-cell weather-table__body-cell_type_humidity']
YX_CALENDAR['pressure'] = ['table.weather-table',
                           'tbody > td.weather-table__body-cell weather-table__body-cell_type_air-pressure']
YX_CALENDAR['wind'] = ['table.weather-table', 'tbody > td.weather-table__body-cell weather-table__'
                                              'body-cell_type_wind weather-table__body-cell_wrapper']
YX_TEMPLATE['current'] = ['div', {'class_': 'fact'}]
YX_TEMPLATE['calendar'] = ['div', {'class_': 'forecast-details i-bem'}]
