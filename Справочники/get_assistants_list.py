# -*- coding: utf-8 -*-
"""
Created on Fri Feb 03 13:40:05 2020

@author: Irina Tretiakova

Получаем список ассистентов

"""

import pandas as pd
import xml.etree.ElementTree as ET
import requests
from datetime import datetime
from settings import TOKEN


headers = {'Authorization': 'OAuth ' + TOKEN}
url = 'https://adfox.yandex.ru/api/v1'

file_name = r'F:\WORK\AdFox\Справочники\DA_assistants_list_{}.xlsx'.format(datetime.now().strftime("%Y-%m-%d-%H%M%S"))

writer = pd.ExcelWriter(file_name)

with writer:
    params = (
        ('object', 'account'),
        ('action', 'list'),
        ('actionObject', 'assistant'),
        ('offset', 0),
        ('limit', 1000),
        ('encoding', 'UTF-8')
    )

    response = requests.get(url, params=params, headers=headers)
    root = ET.fromstring(response.text)

    data = root.find("result").find("data")
    assistants_info_rows = []

    for row in data:
        assistant_data = {}
        for child in list(row):
            try:
                value = int(child.text)
            except:
                value = child.text
            assistant_data[child.tag] = value
        assistants_info_rows.append(assistant_data)

    assistants_info_list = pd.DataFrame(assistants_info_rows)
    assistants_info_list.to_excel(writer, index=False)

print('Отчет готов и находится здесь: {}'.format(file_name))
