# -*- coding: utf-8 -*-
"""
Created on Fri Oct 28 17:44:36 2021

@author: Irina Tretiakova

Получаем инфо о видео баннерах для списка кампаний GPMD

"""

import pandas as pd
import xml.etree.ElementTree as ET
import requests
from datetime import datetime
from settings import ADFOX_API_KEY

headers = {'X-Yandex-API-Key': ADFOX_API_KEY}
url = 'https://adfox.yandex.ru/api/v1'

# ==========Конфиг==========

files_url = r'F:\WORK\AdFox\API_Reports\14.11.2022\\'
in_file = f'{files_url}campaigns.csv'
out_file = f'{files_url}banners_info_{datetime.now().strftime("%Y-%m-%d-%H%M%S")}.xlsx'
campaign_id_field = 'ID кампании'

# =======Конец конфига=======

campaigns_list = pd.read_csv(in_file, encoding='utf8')
campaign_ids_list = campaigns_list[campaign_id_field].to_string(header=False, index=False).\
                                                      replace('\n', ',').replace(' ', '')

limit = 1000

offset = 0
total_rows = limit + 1
page = 0
rows = 0


writer = pd.ExcelWriter(out_file)

with writer:
    while rows + (page - 1) * limit < total_rows:

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

        if page == 1:
            print('total_pages = {}'.format(total_pages))
            print('total_rows = {}'.format(total_rows))
        print(f'Данные страницы {page} запрошены и обрабатываются')

        data = root.find("result").find("data")
        banners_info_rows = []

        for row in data:
            banner_data = {'bannerID': row.find('ID').text,
                           'bannerName': row.find('name').text,
                           'campaignID': row.find('campaignID').text,
                           'campaignName': row.find('campaignName').text,
                           'campaignDateStart': row.find('campaignDateStart').text,
                           'campaignDateEnd': row.find('campaignDateEnd').text,
                           'bannerTypeID': row.find('bannerTypeID').text,
                           'bannerTypeName': row.find('bannerTypeName').text,
                           'status': row.find('status').text,
                           'priority': row.find('priority').text,
                           'isEvents': row.find('isEvents').text,
                           'templateID': row.find('templateID').text,
                           'templateName': row.find('templateName').text,
                           'dateStart': row.find('dateStart').text,
                           'dateAdded': row.find('dateAdded').text}
            for i in range(1, 26):
                parameter = 'parameter' + str(i)
                parameter_name = 'parameter' + str(i) + 'Name'
                banner_data[parameter_name] = '' if row.find(parameter_name) is None else row.find(parameter_name).text
                banner_data[parameter] = '' if row.find(parameter) is None else row.find(parameter).text

            banners_info_rows.append(banner_data)

        if page == 1:
            banners_info_list = pd.DataFrame(banners_info_rows)
        else:
            banners_info_list = banners_info_list.append(pd.DataFrame(banners_info_rows))

        offset += limit
    banners_info_list.to_excel(writer, sheet_name='data')
print(f'Отчет готов и находится здесь: {out_file}')
