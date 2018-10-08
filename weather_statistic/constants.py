# -*- coding: utf-8 -*-

URLS_YANDEX = {'current': 'https://yandex.ru/pogoda/samara/?from=home',
               'calendar': 'https://yandex.ru/pogoda/samara/details?'}

HEROKU_RUN = 'HEROKU_RUN'

YX_CURR_TEMP = 'body > div.b-page__container > div.content > div.content__main > ' \
                    'div.content__row content__row_with-maps-widget_yes > div.fact > div.fact__temp-wrap > ' \
                    'a.link fact__basic day-anchor i-bem > div > span.temp__value'

YX_CURR_CONDITION = 'body > div.b-page__container > div.content > ' \
                        'div.content__main > div.content__row content__row_with-maps-widget_yes > ' \
                        'div.fact > div.fact__temp-wrap > div.fact__condition day-anchor i-bem'

YX_CURR_FEEL = 'body > div.b-page__container > div.content > div.content__main > ' \
                     'div.content__row content__row_with-maps-widget_yes > div.fact > div.fact__temp-wrap > ' \
                     'dl.term term_orient_h fact__feels-like > dd > div > span.temp__value'

YX_CURR_HUMIDITY = 'body > div.b-page__container > div.content > div.content__main > ' \
                  'div.content__row content__row_with-maps-widget_yes > div.fact > ' \
                  'div.fact__props > dl.term term_orient_v fact__humidity > dd'


YX_10DAYS_TEMP = ['body > div.b-page__container > div.content > div.forecast-details i-bem > table.weather-table',
                  'tbody > td.weather-table__body-cell > div.weather-table__temp']

YX_10DAYS_CONDITION = ['body > div.b-page__container > div.content > div.forecast-details i-bem > table.weather-table',
                       'tbody > td.weather-table__body-cell weather-table__body-cell_type_condition']

YX_10DAYS_PRESSURE = ['body > div.b-page__container > div.content > div.forecast-details i-bem > table.weather-table',
                      'tbody > td.weather-table__body-cell weather-table__body-cell_type_air-pressure']

YX_10DAYS_HUMIDITY = ['body > div.b-page__container > div.content > div.forecast-details i-bem > table.weather-table',
                      'tbody > td.weather-table__body-cell weather-table__body-cell_type_humidity']

YX_10DAYS_WIND = ['body > div.b-page__container > div.content > div.forecast-details i-bem > table.weather-table',
                  'tbody > '
                  'td.weather-table__body-cell weather-table__body-cell_type_wind weather-table__body-cell_wrapper']

YX_10DAYS_FEEL = ['body > div.b-page__container > div.content > div.forecast-details i-bem > table.weather-table',
                  'tbody > td.weather-table__body-cell weather-table__body-cell_type_feels-like']
