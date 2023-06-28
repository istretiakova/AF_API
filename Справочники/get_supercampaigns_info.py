# -*- coding: utf-8 -*-
"""
Created on Wen Sep 28 18:56:11 2021

@author: Irina Tretiakova

Получаем общую информацию о суперкампаниях из списка суперкампаний

"""

import pandas as pd
import xml.etree.ElementTree as ET
import requests
from datetime import datetime
from settings import ADFOX_API_KEY

# ===== Начало конфига параметров отчета =====
report_directory = r'F:\WORK\AdFox\API_Reports\26.06.2023'

# указываем название файла со списком ID суперкампаний
supercampaigns_list = pd.read_csv(report_directory + r'\supercampaigns.csv', sep=';', encoding='utf8')

# Указываем имя файла с отчетом, в который будем выгружать данные по API
file_name = report_directory + r'\supercampaigns_info_{}.xlsx'.format(datetime.now().strftime("%Y-%m-%d-%H%M%S"))
# ===== Конец конфига параметров отчета =====

headers = {'X-Yandex-API-Key': ADFOX_API_KEY}
url = 'https://adfox.yandex.ru/api/v1'

supercampaigns_info_rows = []

for supercampaign_num, supercampaign_id in enumerate(supercampaigns_list['ID суперкампании']):
    print(f'{supercampaign_num} -> {supercampaign_id}')
    params = (
        ('object', 'account'),
        ('action', 'list'),
        ('actionObject', 'superCampaign'),
        ('actionObjectID', supercampaign_id),
        ('offset', '0'),
        ('limit', '1000'),
        ('encoding', 'UTF-8')
    )

    response = requests.get(url, params=params, headers=headers)
    root = ET.fromstring(response.text)
    data = root.find("result").find("data")

    for row in data:
        supercampaign_data = {}
        for child in list(row):
            try:
                value = int(child.text)
            except:
                value = child.text
            supercampaign_data[child.tag] = value
        supercampaigns_info_rows.append(supercampaign_data)

campaigns_info = pd.DataFrame(supercampaigns_info_rows)


campaigns_info.to_excel(file_name)
print('Отчет готов и находится здесь: {}'.format(file_name))
