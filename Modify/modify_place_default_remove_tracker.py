# -*- coding: utf-8 -*-
"""
Created on Fri Oct 28 17:44:36 2021

@author: Irina Tretiakova

Изменяем код дефолтного баннера для списка площадок на универсальный

"""

import pandas as pd
import xml.etree.ElementTree as ET
import requests
from datetime import datetime
from settings import ADFOX_API_KEY
import xmltodict
import re

headers = {'X-Yandex-API-Key': ADFOX_API_KEY}
url = 'https://adfox.yandex.ru/api/v1'

# ==========Конфиг==========

files_url = r'F:\WORK\AdFox\API_Reports\25.11.2022\\'
in_file = f'{files_url}places.csv'
out_file = f'{files_url}places_default_trackers_changes_{datetime.now().strftime("%Y-%m-%d-%H%M%S")}.xlsx'

# =======Конец конфига=======

places_list = pd.read_csv(in_file, encoding='utf8')['ID площадки'].tolist()
places_num = len(places_list)
places_changes_data = pd.DataFrame(columns=["placeID", "old_default_code", "new_default_code", "error_code"])

offset = 0
limit = 1000

for n, place_id in enumerate(places_list):

    get_params = (
        ('object', 'account'),
        ('action', 'list'),
        ('actionObject', 'defaultBanner'),
        ('listPlaceIDs', place_id),
        ('offset', offset),
        ('limit', limit),
        ('encoding', 'UTF-8')
    )

    get_response = requests.get(url, params=get_params, headers=headers)
    get_response_dict = xmltodict.parse(get_response.text)

    tracker_for_remove = 'https://www.tns-counter.ru/V13a**%request.eid3%**idsh_vmon/ru/CP1251/' \
                         'tmsec=idsh_dtotal/%request.timestamp%|'

    old_default_code = get_response_dict['response']['result']['data']['row0']['defaultCode']
    new_default_code = old_default_code.replace(tracker_for_remove, '')


    set_params = (
        ('object', 'place'),
        ('action', 'updateDefaultBanner'),
        ('objectID', place_id),
        ('mode', 1),
        ('defaultCode', new_default_code)
    )

    set_response = requests.get(url, params=set_params, headers=headers)
    set_root = ET.fromstring(set_response.text)
    set_error_code = set_root.find("status").find("code").text

    # set_error_code = ''
    print(f'Обрабатывается площадка {n+1} из {places_num} id {place_id}, error code - {set_error_code}')

    place_changes = pd.Series({"placeID": place_id,
                               "old_default_code": old_default_code,
                               "new_default_code": new_default_code,
                               "error_code": set_error_code}
                              )

    places_changes_data = pd.concat([places_changes_data, place_changes.to_frame().T], ignore_index=True)

places_changes_data.to_excel(out_file)
print("Дефолтные баннеры площадок исправлены, отчет об изменениях находится здесь", out_file)
