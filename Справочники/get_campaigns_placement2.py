# -*- coding: utf-8 -*-
"""
Created on Mon Jun 22 18:56:11 2020

@author: Irina Tretiakova

Получаем данные о настройках размещения (placement2) для списка кампаний

"""

import pandas as pd
import xml.etree.ElementTree as ET
import requests
from datetime import datetime
from settings import TOKEN

headers = {'Authorization': 'OAuth ' + TOKEN}
url = 'https://adfox.yandex.ru/api/v1'

campaigns_list = pd.read_csv(r'F:\WORK\AdFox\API_Reports\28.09.2023\campaigns.csv', sep=';', encoding='utf8')

campaigns_placement2_data = pd.DataFrame()
n = 0

for campaign_id in campaigns_list['ID кампании']:
    print('{} -> {}'.format(n, campaign_id))
    n +=1
    params = (
        ('object', 'campaign'),
        ('action', 'info'),
        ('actionObject', 'placement2'),
        ('objectID', campaign_id),
        ('dataType', 'campaignSites'),
        ('isOn', 'on'),
        ('offset', '0'),
        ('limit', '1000'),
        ('encoding', 'UTF-8')
    )
    
   
    response = requests.get(url, params=params, headers=headers)
    root = ET.fromstring(response.text)
    data = root.find("result").find("data")
    
    placement2_data = []
    
    
    try:
        for row in data:
            placement2_site_data = {}
            placement2_site_data['campaign ID'] = campaign_id
            for child in list(row):
                try:
                    value = int(child.text)
                except:
                    value = child.text
                placement2_site_data[child.tag] = value
            placement2_data.append(placement2_site_data)
            campaigns_placement2_data_chunk = pd.DataFrame(placement2_data)
    except:
        print('no data')
        continue
    
    campaigns_placement2_data = pd.concat([campaigns_placement2_data, campaigns_placement2_data_chunk], ignore_index=True)

file_name = r'F:\WORK\AdFox\API_Reports\28.09.2023\campaigns_placement2_{}.xlsx'.format(datetime.now().strftime("%Y-%m-%d-%H%M%S"))
campaigns_placement2_data.to_excel(file_name)
print('Отчет готов и находится здесь: {}'.format(file_name))
