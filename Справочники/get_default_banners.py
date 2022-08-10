# -*- coding: utf-8 -*-
"""
Created on Tue Sep  1 17:17:06 2020

@author: Irina Tretiakova

Получаем данные о дефолтных баннерах по списку площадок
"""


import requests
import pandas as pd
from datetime import datetime
import time
import xml.etree.ElementTree as ET
from settings import ADFOX_API_KEY


list_place_ids = pd.read_excel(r'F:\WORK\Mediascope\2022\промер мобильных приложений\places.xlsx')['ID площадки']

default_banners_info_rows = []

for place_id in list_place_ids:
    url = 'https://adfox.yandex.ru/api/v1'
    
    headers = {
        'X-Yandex-API-Key': ADFOX_API_KEY,
        'Content-Type': 'application/json'
    }
    
    offset = 0
    limit = 1000

    params = (
        ('object','account'),
           ('action','list'),
           ('actionObject','defaultBanner'),
           ('listPlaceIDs', place_id),
           ('offset', offset),
           ('limit', limit),
           ('encoding','UTF-8')
       )
    
    response = requests.get(url, params=params, headers=headers)
    root = ET.fromstring(response.text)
    
    data = root.find("response").find("result").find("data").find('row0')
    
    if data.find('defaultCode').text is not None:
        for row in data:
            default_banner_data = {}
            for child in list(row):
                try:
                    value = int(child.text)
                except:
                    value = child.text
                default_banner_data[child.tag] = value
        default_banners_info_rows.append(default_banner_data)

default_banners_info_list = pd.DataFrame(default_banners_info_rows)

file_name = r'F:\WORK\Mediascope\2022\промер мобильных приложений\DAN_default_banners_info_{}.xlsx'.format(datetime.now().strftime("%Y-%m-%d-%H%M%S"))

with pd.ExcelWriter(file_name) as writer:
    default_banners_info_list.to_excel(writer, sheet_name='default_banners')
    
print('Отчет готов и находится здесь: {}'.format(file_name))