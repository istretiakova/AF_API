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

puid_n = 6

file_name = r'F:\WORK\AdFox\Справочники\DA_user_criteria{}_values_{}.xlsx'\
    .format(puid_n, datetime.now().strftime("%Y-%m-%d-%H%M%S"))


writer = pd.ExcelWriter(file_name)

with writer:
    while rows + (page - 1) * limit < total_rows:
        print('Данные страницы {} запрошены и обрабатываются'.format(page + 1))
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

        total_pages = int(root.find('result').find('total_pages').text)
        page = int(root.find('result').find('page').text)
        total_rows = int(root.find('result').find('total_rows').text)
        rows = int(root.find('result').find('rows').text)

        data = root.find("result").find("data")
        user_criteria_rows = []

        for row in data:
            user_criterias_data = {}
            for child in list(row):
                value = child.text
                user_criterias_data[child.tag] = value
            user_criteria_rows.append(user_criterias_data)

        user_criteria_list = pd.DataFrame(user_criteria_rows)


        if page == 1:
            print('total_pages = {}'.format(total_pages))
            print('total_rows = {}'.format(total_rows))
            user_criteria_list.to_excel(writer, sheet_name='data', index=False)
        else:
            user_criteria_list.to_excel(writer, sheet_name='data', startrow=offset + 1, index=False, header=False)

        offset += limit


print('Отчет готов и находится здесь: {}'.format(file_name))
