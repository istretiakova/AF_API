# -*- coding: utf-8 -*-
"""
Created on Mon Dec 28 17:33:26 2020

@author: Irina Tretiakova

Получаем ГЕО справочник

"""

import pandas as pd
import xml.etree.ElementTree as ET
import requests
from datetime import datetime

key = '4963dde8-b933-47b0-9854-e3a01ea5ebac'
headers = {'X-Yandex-API-Key': key}
url = 'https://adfox.yandex.ru/api/v1'

limit = 1000
offset = 0

total_rows = limit + 1
page = 0
rows = 0

params = (
            ('object', 'account'),
            ('action', 'list'),
            ('actionObject', 'userCriterias'),
            ('offset', offset),
            ('limit', limit),
            ('encoding', 'UTF-8')
        )

response = requests.get(url, params=params, headers=headers)
root = ET.fromstring(response.text)

rows = int(root.find('result').find('rows').text)

data = root.find("result").find("data")