# -*- coding: utf-8 -*-
"""
Created on Sat Jun  6 16:13:11 2020

@author: Irina Tretiakova

Получение по API отчета по сайтам за заданный период и сохраниение его в Excel
"""

import requests
import pandas as pd
from datetime import datetime
import time
import numpy as np

task_url = 'https://adfox.yandex.ru/api/report/owner'
dateFrom = '2021-11-01'
dateTo = '2021-11-30'
key = '4963dde8-b933-47b0-9854-e3a01ea5ebac'

headers = {
    'X-Yandex-API-Key': key,
    'Content-Type': 'application/json'
}

date_range = pd.date_range(start=dateFrom, end=dateTo)
report_table = pd.DataFrame()

for d in date_range:
    date_str = d.strftime("%Y-%m-%d")
    print(date_str)
    params = (
        ('name', 'audienceUsageYa'),
        ('dateFrom', date_str),
        ('dateTo', date_str)
    )

    task_response = requests.get(task_url, params=params, headers=headers)

    report_url = 'https://adfox.yandex.ru/api/report/result?taskId=' + \
                 pd.DataFrame(task_response.json())['result']['taskId']

    report_data = pd.DataFrame({'result': [None]}, index=['state'])

    while report_data.loc['state', 'result'] != 'SUCCESS':
        report_url = 'https://adfox.yandex.ru/api/report/result?taskId=' + pd.DataFrame(task_response.json())['result'][
            'taskId']
        report_response = requests.get(report_url, headers=headers)
        report_data = pd.DataFrame(report_response.json())
        print(report_data.loc['state', 'result'])
        time.sleep(1)
    report_table_chunk = pd.DataFrame(report_data.loc['table', 'result'])
    report_table_chunk['date'] = date_str
    report_table = pd.concat([report_table, report_table_chunk], ignore_index=True)

columns = report_data.loc['fields', 'result']
columns.append('date')
report_table.columns = columns

# report_table = report_table.drop(columns=['correct',
#                           'ownerId',
#                           'loadsDefault',
#                           'clicksDefault',
#                           'ctrCommercial'
#                          ])
# new_index = [
#    'siteId', 
#    'siteName', 
#    'loadsTotal', 
#    'loadsCommercial', 
#    'impressionsCommercial',
#    'clicksCommercial'
#    ]
# report_table = report_table.reindex(columns=new_index)
# report_table = report_table.sort_values(by=['siteId'])

file_name = r'C:\Users\Natalia\Downloads\VN_audienceUsageYa_report_{}.xlsx'.format(
    datetime.now().strftime("%Y-%m-%d-%H%M%S"))
with pd.ExcelWriter(file_name) as writer:
    report_table.to_excel(writer, sheet_name='data')
    pd.pivot_table(report_table, values='impressionsTotal', index=['audienceSegmentName', 'campaignName', 'campaignId'],
                   aggfunc=np.sum).to_excel(writer, sheet_name='pivot1')

print('Отчет готов и находится здесь: {}'.format(file_name))
