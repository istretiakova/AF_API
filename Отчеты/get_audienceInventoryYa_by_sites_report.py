# -*- coding: utf-8 -*-
"""
Created on Tue Sep 15 17:30:54 2021

@author: Irina Tretiakova

Строим отчет по сегментам Я.Аудиторий по списку сайтов

"""

import requests
import pandas as pd
from datetime import datetime
from settings import ADFOX_API_KEY

# ===== Начало конфига параметров отчета =====
date_from = '2023-01-01'
date_to = '2022-01-24'
report_directory = r'F:\WORK\AdFox\API_Reports\25.01.2023'

# В качестве справочника сайтов для постороения отчета берем стандартный отчет по сайтам из Adfox, здесь указываем
# его имя
sites_list = pd.read_excel(report_directory + r'\sites1.xlsx')

# Указываем имя файла с отчетом, в который будем выгружать данные по API
file_name = report_directory + r'\DA_audienceInventoryDMP_by_site_report_{}.xlsx'.format(
    datetime.now().strftime("%Y-%m-%d-%H%M%S"))
# ===== Конец конфига параметров отчета =====

report_headers = {
    'X-Yandex-API-Key': ADFOX_API_KEY,
    'Content-Type': 'application/json'
}

sites_list = sites_list.set_index('ID сайта').dropna()

report_table = pd.DataFrame()
sites_num = len(sites_list)
site_num = 1
report_table_len = 0

writer = pd.ExcelWriter(file_name)

with writer:
    for site_id, site_name in sites_list['Название сайта'].items():
        site_id = int(site_id)
        report_data = pd.DataFrame({'result': [None]}, index=['state'])
        print(f'запрашиваем данные {site_num} сайта из {sites_num}: {site_id} {site_name}')

        report_params = {
            'name': 'audienceInventoryDmp',
            'dateFrom': date_from,
            'dateTo': date_to,
            'siteId': site_id,
            'audienceSegments': ''
        }

        task_response = requests.get('https://adfox.yandex.ru/api/report/site',
                                     params=report_params, headers=report_headers)
        print(pd.DataFrame(task_response.json())['result']['taskId'])

        while report_data.loc['state', 'result'] != 'SUCCESS':
            report_url = 'https://adfox.yandex.ru/api/report/result?taskId=' + \
                         pd.DataFrame(task_response.json())['result']['taskId']
            report_response = requests.get(report_url, headers=report_headers)
            report_data = pd.DataFrame(report_response.json())

        report_table_chunk = pd.DataFrame(report_data.loc['table', 'result'],
                                          columns=report_data.loc['fields', 'result'])
        report_table_chunk['siteId'] = site_id
        report_table_chunk['siteName'] = site_name

        report_table_chunk_len = report_table_chunk.index.__len__()

        if site_num == 1:
            report_table_chunk.to_excel(writer, sheet_name='data', index=False)
        else:
            report_table_chunk.to_excel(writer, sheet_name='data', startrow=report_table_len + 1, header=False,
                                        index=False)

        report_table_len += report_table_chunk_len
        site_num += 1

print('Отчет готов и находится здесь: {}'.format(file_name))
