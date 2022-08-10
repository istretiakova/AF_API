# -*- coding: utf-8 -*-
"""
Created on Tue Sep  1 17:17:06 2020

@author: Irina Tretiakova

Получаем данные о дефолтных баннерах по списку площадок
"""

import requests
import pandas as pd
from datetime import datetime
import xmltodict
from settings import ADFOX_API_KEY

list_place_ids = pd.read_excel(r'F:\WORK\AdFox\API_Reports\05.07.2022\places.xlsx')['ID площадки']

default_banners_info_rows = []

print(f'Количество площадок = {list_place_ids.index.size}')
place_num = 1

for place_id in list_place_ids:

    print(f'Получаем данные по {place_num} площадке из {list_place_ids.index.size} - place_id = {place_id}')
    place_num += 1
    url = 'https://adfox.yandex.ru/api/v1'

    headers = {
        'X-Yandex-API-Key': ADFOX_API_KEY,
        'Content-Type': 'application/json'
    }

    offset = 0
    limit = 1000

    params = (
        ('object', 'account'),
        ('action', 'list'),
        ('actionObject', 'defaultBanner'),
        ('listPlaceIDs', place_id),
        ('offset', offset),
        ('limit', limit),
        ('encoding', 'UTF-8')
    )

    response = requests.get(url, params=params, headers=headers)
    response_dict = xmltodict.parse(response.text)

    data = response_dict['response']['result']['data']['row0']
    if data['defaultCode'] is not None:
        default_banner_data = {}
        for item in data.items():
            default_banner_data[item[0]] = item[1]
        default_banners_info_rows.append(default_banner_data)

default_banners_info_list = pd.DataFrame(default_banners_info_rows)

file_name = r'F:\WORK\AdFox\API_Reports\05.07.2022\default_banners_info_{}.xlsx'.format(
    datetime.now().strftime("%Y-%m-%d-%H%M%S"))

with pd.ExcelWriter(file_name) as writer:
    default_banners_info_list.to_excel(writer, sheet_name='default_banners')

print('Отчет готов и находится здесь: {}'.format(file_name))