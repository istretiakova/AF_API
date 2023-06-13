# -*- coding: utf-8 -*-
"""
Created on Mon Jun 22 18:00:54 2020

@author: Irina Tretiakova

Получаем данные о таргетировании для списка баннеров

"""

import pandas as pd
import xml.etree.ElementTree as ET
import requests
from datetime import datetime
from settings import ADFOX_API_KEY

# ===== Начало конфига параметров отчета =====
report_directory = r'F:\WORK\AdFox\API_Reports\21.03.2023'

# указываем название файла со списком ID кампаний
banners_list = pd.read_csv(report_directory + r'\test_tp_banners.csv', sep='\t', encoding='utf8')

# Указываем имя файла с отчетом, в который будем выгружать данные по API
file_name = report_directory + r'\banners_targeting_{}.xlsx'\
    .format(datetime.now().strftime("%Y-%m-%d-%H%M%S"))
# ===== Конец конфига параметров отчета =====

headers = {'X-Yandex-API-Key': ADFOX_API_KEY}
url = 'https://adfox.yandex.ru/api/v1'

banners_targeting_data = pd.DataFrame()
n = 1
banners_num = banners_list.index.size
for banner_id in banners_list['ID баннера']:
    params = (
        ('object', 'banner'),
        ('action', 'info'),
        ('actionObject', 'targeting'),
        ('objectID', banner_id)
    )
    response = requests.get(url, params=params, headers=headers)
    root = ET.fromstring(response.text)
    data = root.find("result").find("data")
    targeting_data = []
    targeting_criteria = {}
    targeting_criteria['banner ID'] = banner_id
    print('Выполнено на {}% -> Баннер {} из {} id {}, error code - {}'
          .format(round(n/banners_num*100, 1), n, banners_num, banner_id, root.find("status").find("code").text))
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
    banners_targeting_data_chunk = pd.DataFrame(targeting_data)
    banners_targeting_data = pd.concat([banners_targeting_data, banners_targeting_data_chunk], ignore_index=True)


banners_targeting_data.to_excel(file_name)
print("Отчет готов и находится здесь", file_name)


