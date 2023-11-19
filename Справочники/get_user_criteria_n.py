# -*- coding: utf-8 -*-
"""
Created on Wed Jul 06 14:05:26 2022

@author: Irina Tretiakova

Получаем справочник пользовательского таргетирования puidN

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

puid_n = 60

params = (
            ('object', 'userCriteria'),
            ('action', 'listValues'),
            ('criteriaID', puid_n),
            ('offset', offset),
            ('limit', limit),
            ('encoding', 'UTF-8')
        )

response = requests.get(url, params=params, headers=headers)
root = ET.fromstring(response.text)

data = root.find("result").find("data")
user_criteria_rows = []

for row in data:
    user_criterias_data = {}
    for child in list(row):
        value = child.text
        user_criterias_data[child.tag] = value
    user_criteria_rows.append(user_criterias_data)

user_criteria_list = pd.DataFrame(user_criteria_rows)


file_name = r'F:\WORK\AdFox\Справочники\DA_user_criteria{}_values_{}.xlsx'\
    .format(puid_n, datetime.now().strftime("%Y-%m-%d-%H%M%S"))

user_criteria_list.to_excel(file_name)
print('Отчет готов и находится здесь: {}'.format(file_name))
