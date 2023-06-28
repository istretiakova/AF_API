# -*- coding: utf-8 -*-
"""
Created on Wen Sep 22 18:56:11 2021

@author: Irina Tretiakova

Получаем общую информацию о кампаниях из списка кампаний

"""

import pandas as pd
import xml.etree.ElementTree as ET
import requests
from datetime import datetime
from settings import ADFOX_API_KEY

headers = {'X-Yandex-API-Key': ADFOX_API_KEY}
url = 'https://adfox.yandex.ru/api/v1'

campaigns_list = pd.read_csv(r'F:\WORK\AdFox\API_Reports\26.06.2023\campaigns.csv', sep=';', encoding='utf8')
n = 1

campaigns_info_rows = []

for campaign_id in campaigns_list['ID кампании']:
    print(f'{n} -> {campaign_id}')
    n += 1
    params = (
        ('object', 'account'),
        ('action', 'list'),
        ('actionObject', 'campaign'),
        ('actionObjectID', campaign_id),
        ('offset', '0'),
        ('limit', '1000'),
        ('encoding', 'UTF-8')
    )

    response = requests.get(url, params=params, headers=headers)
    root = ET.fromstring(response.text)
    data = root.find("result").find("data")

    for row in data:
        campaign_data = {}
        for child in list(row):
            try:
                value = int(child.text)
            except:
                value = child.text
            campaign_data[child.tag] = value
        campaigns_info_rows.append(campaign_data)

campaigns_info = pd.DataFrame(campaigns_info_rows)

file_name = r'F:\WORK\AdFox\API_Reports\26.06.2023\campaigns_info_{}.xlsx'.\
    format(datetime.now().strftime("%Y-%m-%d-%H%M%S"))
campaigns_info.to_excel(file_name)
print('Отчет готов и находится здесь: {}'.format(file_name))
