# -*- coding: utf-8 -*-
"""
Created on Fri Jul 10 17:44:36 2020

@author: Irina Tretiakova

Получаем инфо инфо о баннерах для списка кампаний

"""

import pandas as pd
import xml.etree.ElementTree as ET
import requests
from datetime import datetime
from settings import ADFOX_API_KEY

headers = {'X-Yandex-API-Key': ADFOX_API_KEY}
url = 'https://adfox.yandex.ru/api/v1'

campaigns_list = pd.read_csv(r'F:\WORK\AdFox\API_Reports\01.06.2023\sizmek_campaigns.csv', sep='\t', encoding='utf8')
campaign_ids_list = campaigns_list['ID кампании'].to_string(header=False, index=False).replace('\n', ',').replace(' ',
                                                                                                                  '')

limit = 1000

offset = 0
total_rows = limit + 1
page = 0
rows = 0

file_name = r'F:\WORK\AdFox\API_Reports\01.06.2023\sizmek_banners_info_{}.xlsx'.\
    format(datetime.now().strftime("%Y-%m-%d-%H%M%S"))

writer = pd.ExcelWriter(file_name)

with writer:
    while rows + (page - 1) * limit < total_rows:
        print('Данные страницы {} запрошены и обрабатываются'.format(page + 1))
        params = (
            ('object', 'account'),
            ('action', 'list'),
            ('actionObject', 'banner'),
            ('listCampaignIDs', campaign_ids_list),
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
        banners_info_rows = []

        for row in data:
            banner_data = {}
            for child in list(row):
                try:
                    value = int(child.text)
                except:
                    value = child.text
                banner_data[child.tag] = value
            banners_info_rows.append(banner_data)

        banners_info_list = pd.DataFrame(banners_info_rows)
        if page == 1:
            print('total_pages = {}'.format(total_pages))
            print('total_rows = {}'.format(total_rows))
            # banners_info_list.to_excel(writer, sheet_name = 'data', index = False)
            banners_info_list.to_excel(writer, sheet_name='data')
        else:
            # banners_info_list.to_excel(writer, sheet_name = 'data', startrow = offset+1, header = False,
            # index = False)
            banners_info_list.to_excel(writer, sheet_name='data', startrow=offset + 5)

        offset += limit

print('Отчет готов и находится здесь: {}'.format(file_name))
