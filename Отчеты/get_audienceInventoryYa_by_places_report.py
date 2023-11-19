# -*- coding: utf-8 -*-
"""
Created on Tue Jul 14 16:36:54 2020

@author: Irina Tretiakova

Строим отчет по сегментам Я.Аудиторий по списку площадок

"""

import requests
import pandas as pd
from datetime import datetime
from settings import ADFOX_API_KEY

date_from = '2021-12-01'
date_to = '2021-12-16'

report_headers = {
    'X-Yandex-API-Key': ADFOX_API_KEY,
    'Content-Type': 'application/json'
}

active_places_list = pd.read_excel(
    r'F:\WORK\AdFox\Справочники\IMN_300x250_places.xlsx',
    sheet_name='active_places')

active_places_list = active_places_list.set_index('placeId')

report_table = pd.DataFrame()
places_num = active_places_list.index.__len__()
place_num = 1
report_table_len = 0

file_name = r'C:\Users\Natalia\Downloads\IPN_audienceInventoryYa_report_{}.xlsx'.format(
    datetime.now().strftime("%Y-%m-%d-%H%M%S"))
writer = pd.ExcelWriter(file_name)

with writer:
    for place_id in active_places_list.index:

        place_name = active_places_list.loc[place_id]['placeName']
        section_id = active_places_list.loc[place_id]['sectionId']
        section_name = active_places_list.loc[place_id]['sectionName']
        site_id = active_places_list.loc[place_id]['siteId']
        site_name = active_places_list.loc[place_id]['siteName']

        report_data = pd.DataFrame({'result': [None]}, index=['state'])

        print('запрашиваем данные {} площадки из {}: '
              'siteId {} {} / sectionId {} {} / placeId {} {}'.format(place_num,
                                                                      places_num,
                                                                      site_id,
                                                                      site_name,
                                                                      section_id,
                                                                      section_name,
                                                                      place_id,
                                                                      place_name))

        report_params = {
            'name': 'audienceInventoryYa',
            'placeId': place_id,
            'dateFrom': date_from,
            'dateTo': date_to
        }

        task_response = requests.get('https://adfox.yandex.ru/api/report/place',
                                     params=report_params, headers=report_headers)
        print(pd.DataFrame(task_response.json())['result']['taskId'])

        report_url = 'https://adfox.yandex.ru/api/report/result?taskId=' + \
                         pd.DataFrame(task_response.json())['result']['taskId']
        report_response = requests.get(report_url, headers=report_headers)
        report_data = pd.DataFrame(report_response.json())

        report_table_chunk = pd.DataFrame(report_data.loc['table', 'result'],
                                          columns=report_data.loc['fields', 'result'])
        report_table_chunk['siteId'] = site_id
        report_table_chunk['siteName'] = site_name
        report_table_chunk['sectionId'] = section_id
        report_table_chunk['sectionName'] = section_name
        report_table_chunk['placeId'] = place_id
        report_table_chunk['placeName'] = place_name

        report_table_chunk_len = report_table_chunk.index.__len__()

        if place_num == 1:
            report_table_chunk.to_excel(writer, sheet_name='data', index=False)
        else:
            report_table_chunk.to_excel(writer, sheet_name='data', startrow=report_table_len + 1, header=False,
                                        index=False)

        report_table_len += report_table_chunk_len
        place_num += 1

print('Отчет готов и находится здесь: {}'.format(file_name))
