# -*- coding: utf-8 -*-
"""
Created on Fri Oct 28 17:44:36 2021

@author: Irina Tretiakova

Изменяем код дефолтного баннера для списка площадок на универсальный wrapper с уникальным пассбэк-тегом паблишера

"""

import pandas as pd
import xml.etree.ElementTree as ET
import requests
from settings import ADFOX_API_KEY

headers = {'X-Yandex-API-Key': ADFOX_API_KEY}
url = 'https://adfox.yandex.ru/api/v1'

# ==========Конфиг==========

files_url = r'F:\WORK\AdFox\API_Reports\17.01.2023\\'
in_file = f'{files_url}places.csv'

# =======Конец конфига=======

places_list = pd.read_csv(in_file, encoding='utf8')['ID площадки'].tolist()
places_num = len(places_list)

for n, place_id in enumerate(places_list):

    set_params = (
        ('object', 'place'),
        ('action', 'modify'),
        ('objectID', place_id),
        ('pct', 4)
    )

    set_response = requests.get(url, params=set_params, headers=headers)
    set_root = ET.fromstring(set_response.text)
    set_error_code = set_root.find("status").find("code").text

    print(f'Обрабатывается площадка {n+1} из {places_num} id {place_id}, error code - {set_error_code}')

print("PCT для площадок исправлены")
