# -*- coding: utf-8 -*-

import os
import time
import psycopg2
from weather_statistic.constants import (URLS_YANDEX,
                                         HEROKU_RUN)
from weather_statistic.constants_private import *
from weather_statistic.html_data import YxWeather


def heroku_detect(config_vars):
    if config_vars in os.environ:
        return True
    else:
        return False


def create_connection_sql():  # TODO Добавить обработку исключений
    if heroku_detect(HEROKU_RUN):
        return psycopg2.connect(database=DATABASE_HEROKU, user=USER_HEROKU,
                                password=PASSWORD_HEROKU,
                                host=HOST_HEROKU, port=PORT, sslmode='require')
    else:
        return psycopg2.connect(database=DATABSE_TEST, user=USER_LOCAL,
                                password=PASSWORD_LOCAL, host=HOST_LOCAL,
                                port=PORT)


if __name__ == '__main__':
    yx = YxWeather(URLS_YANDEX)
    while True:
        print(yx.update_and_get_different())
        time.sleep(100)
    connection_sql = create_connection_sql()
    cursor_sql = connection_sql.cursor()
