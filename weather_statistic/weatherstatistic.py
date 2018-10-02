# -*- coding: utf-8 -*-

import os
import psycopg2
from weather_statistic import constants
from weather_statistic import constants_private


def heroku_detect(config_vars):
    if config_vars in os.environ:
        return True
    else:
        return False


def create_connetion_sql():
    if heroku_detect(constants.HEROKU_RUN):
        return psycopg2.connect(database=constants_private.DATABASE_HEROKU, user=constants_private.USER_HEROKU,
                                password=constants_private.PASSWORD_HEROKU,
                                host=constants_private.HOST_HEROKU, port=constants_private.PORT, sslmode='require')
    else:
        return psycopg2.connect(database=constants_private.DATABSE_TEST, user=constants_private.USER_LOCAL,
                                password=constants_private.PASSWORD_LOCAL, host=constants_private.HOST_LOCAL,
                                port=constants_private.PORT)


if __name__ == '__main__':
    connection_sql = create_connetion_sql()
    cursor_sql = connection_sql.cursor()
