# -*- coding: utf-8 -*-
"""
Created on Fry Apr 01 17:44:56 2021

@author: Irina Tretiakova

Получаем список Кампаний за период с date_from

"""

import pandas as pd
import xml.etree.ElementTree as ET
import requests
from datetime import datetime

key = '4963dde8-b933-47b0-9854-e3a01ea5ebac'
headers = {'X-Yandex-API-Key': key}
url = 'https://adfox.yandex.ru/api/v1'

date_from = '2022-03-28'

limit = 1000

offset = 0
total_rows = limit + 1
page = 0
rows = 0

file_name = r'F:\WORK\AdFox\API_Reports\01.04.2022\campaigns_{}.xlsx'.format(
    datetime.now().strftime("%Y-%m-%d-%H%M%S"))

writer = pd.ExcelWriter(file_name)

with writer:
    while rows + (page - 1) * limit < total_rows:
        print('Данные страницы {} запрошены и обрабатываются'.format(page + 1))

        params = (
            ('object', 'account'),
            ('action', 'list'),
            ('actionObject', 'campaign'),
            ('dateAddedFrom', date_from),
            ('offset', offset),
            ('limit', limit),
            ('encoding', 'UTF-8')
        )

        response = requests.get(url, params=params, headers=headers)
        root = ET.fromstring(response.text)

        total_pages = int(root.find('result').find('total_pages').text)
        page = int(root.find('result').find('page').text)
        total_rows = int(root.find('result').find('total_rows').text)
        rows = int(root.find('result').find('rows').text)

        data = root.find("result").find("data")
        supercampaigns_info_rows = []

        for row in data:
            supercampaign_data = {}
            for child in list(row):
                try:
                    value = int(child.text)
                except:
                    value = child.text
                supercampaign_data[child.tag] = value
            supercampaigns_info_rows.append(supercampaign_data)

        supercampaigns_info_list = pd.DataFrame(supercampaigns_info_rows)
        if page == 1:
            print('total_pages = {}'.format(total_pages))
            print('total_rows = {}'.format(total_rows))
            supercampaigns_info_list.to_excel(writer, sheet_name='data', index=False)
        else:
            supercampaigns_info_list.to_excel(writer, sheet_name='data', startrow=offset + 1, header=False, index=False)

        offset += limit

print('Отчет готов и находится здесь: {}'.format(file_name))
