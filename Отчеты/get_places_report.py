# -*- coding: utf-8 -*-
"""
Created on Fri Jun 26 12:19:26 2020

@author: Irina Tretiakova

Получение отчета по открутке по списку площадок
"""

import requests
import pandas as pd
from datetime import datetime
from settings import ADFOX_API_KEY

# Указать файл, полученный при помощи скрипта get_places_list.py
places_list = pd.read_excel(r'F:\WORK\AdFox\API_Reports\25.01.2023\places_info.xlsx', index_col=0)
date_from = '2023-01-24'
date_to = '2023-01-24'

days_report_table = pd.DataFrame()
days_headers = {
    'X-Yandex-API-Key': ADFOX_API_KEY,
    'Content-Type': 'application/json'
}

days_report_rows = []
days_report_cols = [
    'siteID',
    'siteName',
    'sectionID',
    'sectionName',
    'placeID',
    'placeName',
    'loadsTotal',
    'loadsCommercial',
    'impressionsCommercial',
    'loadsDefault',
    'clicksCommercial'
]

print('Количество площадок = {}'.format(places_list.index.size))
place_num = 1
for place_id in places_list.index:
    print('получаем инфо по {} площадке из {}'.format(place_num, places_list.index.size))
    place_num += 1
    place_name = places_list.loc[place_id]['name']
    site_id = places_list.loc[place_id]['siteID']
    site_name = places_list.loc[place_id]['siteName']
    section_id = places_list.loc[place_id]['zoneID']
    section_name = places_list.loc[place_id]['zoneName']

    days_report_data = pd.DataFrame({'result': [None]}, index=['state'])

    days_params = (
        ('name', 'days'),
        ('placeId', place_id),
        ('dateFrom', date_from),
        ('dateTo', date_to)
    )

    days_task_response = requests.get('https://adfox.yandex.ru/api/report/place',
                                                        params=days_params,
                                                        headers=days_headers)

    try:
        while days_report_data.loc['state', 'result'] != 'SUCCESS':
            days_report_url = 'https://adfox.yandex.ru/api/report/result?taskId=' + \
                                                pd.DataFrame(days_task_response.json())['result'][
                                                    'taskId']
            days_report_response = requests.get(days_report_url, headers=days_headers)
            days_report_data = pd.DataFrame(days_report_response.json())
            # time.sleep(0.5)

        try:
            loadsTotal = int(days_report_data.loc['totals']['result']['loadsTotal'])
            loadsCommercial = int(days_report_data.loc['totals']['result']['loadsCommercial'])
            impressionsCommercial = int(days_report_data.loc['totals']['result']['impressionsCommercial'])
            loadsDefault = int(days_report_data.loc['totals']['result']['loadsDefault'])
            clicksCommercial = int(days_report_data.loc['totals']['result']['clicksCommercial'])
        except:
            continue
    except:
        continue

    if loadsTotal > 0:
        days_report_rows.append({
            'siteID': site_id,
            'siteName': site_name,
            'sectionID': section_id,
            'sectionName': section_name,
            'placeID': place_id,
            'placeName': place_name,
            'loadsTotal': loadsTotal,
            'loadsCommercial': loadsCommercial,
            'impressionsCommercial': impressionsCommercial,
            'loadsDefault': loadsDefault,
            'clicksCommercial': clicksCommercial
        })

days_report = pd.DataFrame(days_report_rows, columns=days_report_cols)
file_name = r'F:\WORK\Объединение с ГПМД\Справочники\GPMD_places_report_oct-nov2020_{}.xlsx'.format(
    datetime.now().strftime("%Y-%m-%d-%H%M%S"))
days_report.to_excel(file_name)
print('places_report - SUCCESS, report is here: {}'.format(file_name))