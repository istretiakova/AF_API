# -*- coding: utf-8 -*-
"""
Created on Fri Jun 26 12:19:26 2020

@author: Irina Tretiakova

Получение отчета по запросам по HeaderBidding по списку площадок
"""

import requests
import pandas as pd
from datetime import datetime
import time

# Указать файл, полученный при помощи скрипта get_places_report.py
places_list = pd.read_excel(r'C:\Users\Natalia\Downloads\IMN_places_report_jul-oct2020_2020-10-14-174720.xlsx', index_col=0)
key = '5313a9e4-5ab7-4742-b292-39602532534f'
date_from = '2020-07-01'
date_to = '2020-10-14'

headerBiddingDaysAdfox_report_table = pd.DataFrame()
headerBiddingDaysAdfox_headers = {
    'X-Yandex-API-Key': key,
    'Content-Type': 'application/json'
}

headerBiddingDaysAdfox_report_rows = []
headerBiddingDaysAdfox_report_cols = [
    'siteID',
    'siteName',
    'sectionID',
    'sectionName',
    'placeID',
    'placeName',
    'requestsHB'
]

print('Количество площадок = {}'.format(places_list.index.size))
place_num = 1
places_list = places_list.set_index('placeID')
for place_id in places_list.index:
    print('получаем инфо по {} площадке из {}'.format(place_num, places_list.index.size))
    place_num += 1
    place_name = places_list.loc[place_id]['placeName']
    site_id = places_list.loc[place_id]['siteID']
    site_name = places_list.loc[place_id]['siteName']
    section_id = places_list.loc[place_id]['sectionID']
    section_name = places_list.loc[place_id]['sectionName']

    headerBiddingDaysAdfox_report_data = pd.DataFrame({'result': [None]}, index=['state'])

    headerBiddingDaysAdfox_params = (
        ('name', 'headerBiddingDaysAdfox'),
        ('placeId', place_id),
        ('dateFrom', date_from),
        ('dateTo', date_to)
    )

    headerBiddingDaysAdfox_task_response = requests.get('https://adfox.yandex.ru/api/report/place',
                                                        params=headerBiddingDaysAdfox_params,
                                                        headers=headerBiddingDaysAdfox_headers)

    while headerBiddingDaysAdfox_report_data.loc['state', 'result'] != 'SUCCESS':
        headerBiddingDaysAdfox_report_url = 'https://adfox.yandex.ru/api/report/result?taskId=' + \
                                            pd.DataFrame(headerBiddingDaysAdfox_task_response.json())['result'][
                                                'taskId']
        headerBiddingDaysAdfox_report_response = requests.get(headerBiddingDaysAdfox_report_url,
                                                              headers=headerBiddingDaysAdfox_headers)
        headerBiddingDaysAdfox_report_data = pd.DataFrame(headerBiddingDaysAdfox_report_response.json())
        # time.sleep(0.5)

    try:
        loadsHbIgnored = int(headerBiddingDaysAdfox_report_data.loc['totals']['result']['loadsHbIgnored'])
    except:
        continue

    if loadsHbIgnored > 0:
        headerBiddingDaysAdfox_report_rows.append({
            'siteID': site_id,
            'siteName': site_name,
            'sectionID': section_id,
            'sectionName': section_name,
            'placeID': place_id,
            'placeName': place_name,
            'requestsHB': loadsHbIgnored
        })

headerBiddingDaysAdfox_report = pd.DataFrame(headerBiddingDaysAdfox_report_rows,
                                             columns=headerBiddingDaysAdfox_report_cols)
file_name = r'C:\Users\Natalia\Downloads\IMN_headerBiddingDaysAdfox_by_places_report_jul-oct2020_{}.xlsx'. \
    format(datetime.now().strftime("%Y-%m-%d-%H%M%S"))
headerBiddingDaysAdfox_report.to_excel(file_name)
print('headerBiddingDaysAdfox_report - SUCCESS, report is here: {}'.format(file_name))
