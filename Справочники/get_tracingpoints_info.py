# -*- coding: utf-8 -*-
"""
Created on Tue Mar 22 12:01:11 2022

@author: Irina Tretiakova

Получаем данные о точках учета действий

"""

import pandas as pd
import xml.etree.ElementTree as ET
import requests
from datetime import datetime
from settings import ADFOX_API_KEY

# ===== Начало конфига параметров отчета =====
# Название файла с выгрузкой
file_name = r'F:\WORK\AdFox\Справочники\DA_tracingpoints_info_{}.xlsx'.\
    format(datetime.now().strftime("%Y-%m-%d-%H%M%S"))

# ID рекламодателя AdFox для фильтра. Если нужны все точки, то оставить пустым: advertiser_id = ''
advertiser_id = ''
# ===== Конец конфига параметров отчета =====

a_lowercase = ord('a')
alfabet_size = 26

def _decompose(number):
    """Generate digits from `number` in base alphabet, least significants
    bits first.

    Since A is 1 rather than 0 in base alphabet, we are dealing with
    `number - 1` at each iteration to be able to extract the proper digits.
    """

    while number:
        number, remainder = divmod(number, alfabet_size)
        yield remainder


def base_10_to_alphabet(number):
    """Convert a decimal number to its base alphabet representation"""

    return ''.join(
        chr(a_lowercase + part)
        for part in _decompose(number)
    )[::-1]


headers = {'X-Yandex-API-Key': ADFOX_API_KEY}
url = 'https://adfox.yandex.ru/api/v1'

limit = 1000
offset = 0

total_rows = limit + 1
page = 0
rows = 0

writer = pd.ExcelWriter(file_name)

with writer:
    while rows + (page - 1) * limit < total_rows:
        print('Данные страницы {} запрошены и обрабатываются'.format(page + 1))

        params = (
            ('object', 'account'),
            ('action', 'list'),
            ('actionObject', 'tracingPoint'),
            ('advertiserID', advertiser_id),
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
        tracingPoints_info_rows = []

        for row in data:
            tracingPoint_data = {}
            for child in list(row):
                try:
                    value = int(child.text)
                except:
                    value = child.text
                tracingPoint_data[child.tag] = value
            p7 = base_10_to_alphabet(int(row.find(
                "advertiserID").text)) if row.find("advertiserID").text is not None else 0
            tracingPoint_data['p7 (advertiserID base26)'] = p7
            p8 = base_10_to_alphabet(
                int(row.find("userID").text)) if row.find("userID").text is not None else 0
            tracingPoint_data['p8 (userID base26)'] = p8
            tracingPoint_data['tracePoint Tag'] = f"https://yandex.ru/ads/adfox/226279/tracePoint?p7={p7}&p8={p8}"
            tracingPoints_info_rows.append(tracingPoint_data)

        tracingPoints_info_list = pd.DataFrame(tracingPoints_info_rows)
        if page == 1:
            print('total_pages = {}'.format(total_pages))
            print('total_rows = {}'.format(total_rows))
            tracingPoints_info_list.to_excel(writer, sheet_name='data', index=False)
        else:
            tracingPoints_info_list.to_excel(writer, sheet_name='data', startrow=offset + 1, header=False, index=False)

        offset += limit

print('Отчет готов и находится здесь: {}'.format(file_name))
