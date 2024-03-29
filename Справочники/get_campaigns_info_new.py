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
from settings import TOKEN

# ===== Начало конфига параметров отчета =====
report_directory = r'F:\WORK\AdFox\API_Reports\16.02.2024'

# указываем название файла со списком ID суперкампаний
campaigns_list = pd.read_csv(report_directory + r'\nra_campaigns_feb2024.csv', sep=';', encoding='utf8')

# Указываем имя файла с отчетом, в который будем выгружать данные по API
file_name = report_directory + r'\campaigns_info_{}.xlsx'.format(datetime.now().strftime("%Y-%m-%d-%H%M%S"))
# ===== Конец конфига параметров отчета =====

headers = {'Authorization': 'OAuth ' + TOKEN}
url = 'https://adfox.yandex.ru/api/v1'

campaigns_info_rows = []

for campaign_num, campaign_id in enumerate(campaigns_list['ID кампании']):
    print(f'{campaign_num} -> {campaign_id}')
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


campaigns_info.to_excel(file_name)
print('Отчет готов и находится здесь: {}'.format(file_name))
