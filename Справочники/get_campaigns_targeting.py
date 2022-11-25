# -*- coding: utf-8 -*-
"""
Created on Mon Jun 22 18:00:54 2020

@author: Irina Tretiakova

Получаем данные о таргетировании для списка кампаний

"""

import pandas as pd
import xml.etree.ElementTree as ET
import requests
from datetime import datetime
from settings import ADFOX_API_KEY

# ===== Начало конфига параметров отчета =====
report_directory = r'F:\WORK\AdFox\API_Reports\15.11.2022'

# указываем название файла со списком ID кампаний
campaigns_list = pd.read_csv(report_directory + r'\campaigns.csv', sep='\t', encoding='utf8')

# Указываем имя файла с отчетом, в который будем выгружать данные по API
file_name = report_directory + r'\campaigns_targeting_{}.xlsx'\
    .format(datetime.now().strftime("%Y-%m-%d-%H%M%S"))
# ===== Конец конфига параметров отчета =====

headers = {'X-Yandex-API-Key': ADFOX_API_KEY}
url = 'https://adfox.yandex.ru/api/v1'

campaigns_targeting_data = pd.DataFrame()
n = 1
campaigns_num = campaigns_list.index.size
for campaign_id in campaigns_list['ID кампании']:
    params = (
        ('object', 'campaign'),
        ('action', 'info'),
        ('actionObject', 'targeting'),
        ('objectID', campaign_id)
    )
    response = requests.get(url, params=params, headers=headers)
    root = ET.fromstring(response.text)
    data = root.find("result").find("data")
    targeting_data = []
    targeting_criteria = {}
    targeting_criteria['campaign ID'] = campaign_id
    print('Выполнено на {}% -> Кампания {} из {} id {}, error code - {}'
          .format(round(n/campaigns_num*100, 1), n, campaigns_num, campaign_id, root.find("status").find("code").text))
    n += 1
    for row in data:
        if row.find("name").text == 'UDP':
            targeting_criteria['UDP gender'] = row.find("description").find("gender").text.replace("По полу: ", "") \
                if row.find("description").find("gender").text != "По полу: не задано" else ""
            targeting_criteria['UDP age'] = row.find("description").find("age").text.replace("По возрасту: ", "") \
                if row.find("description").find("age").text != "По возрасту: не задано" else ""
            targeting_criteria['UDP revenue'] = row.find("description").find("revenue").text.replace("По доходу: ", "")\
                if row.find("description").find("revenue").text != "По доходу: не задано" else ""
        else:
            targeting_criteria[row.find("name").text] = row.find("description").text \
                if row.find("description").text != "не&nbsp;задано" else ""
    targeting_data.append(targeting_criteria)
    campaigns_targeting_data_chunk = pd.DataFrame(targeting_data)
    campaigns_targeting_data = pd.concat([campaigns_targeting_data, campaigns_targeting_data_chunk], ignore_index=True)


campaigns_targeting_data.to_excel(file_name)
print("Отчет готов и находится здесь", file_name)


