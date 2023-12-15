# -*- coding: utf-8 -*-
"""
Created on Mon Jul 13 17:31:26 2020

@author: Irina Tretiakova

Получаем списко справочников пользовательского таргетирования

"""

import pandas as pd
import xml.etree.ElementTree as ET
import requests
from datetime import datetime
from settings import TOKEN

headers = {'Authorization': 'OAuth ' + TOKEN}
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
user_criterias_list_rows = []

for row in data:
    user_criterias_data = {}
    for child in list(row):
        value = child.text
        user_criterias_data[child.tag] = value
    user_criterias_list_rows.append(user_criterias_data)

user_criterias_list = pd.DataFrame(user_criterias_list_rows)


file_name = r'F:\WORK\AdFox\Справочники\DA_user_criterias_list_{}.xlsx'\
    .format(datetime.now().strftime("%Y-%m-%d-%H%M%S"))

user_criterias_list.to_excel(file_name)
print('Отчет готов и находится здесь: {}'.format(file_name))
