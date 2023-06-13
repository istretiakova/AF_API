# -*- coding: utf-8 -*-
"""
Created on Tue Jun 13 12:19:26 2022

@author: Irina Tretiakova

Получение кастомного отчета
"""

import requests
import pandas as pd
from datetime import datetime, timedelta
import xlsxwriter
from settings import ADFOX_API_KEY


headers = {'X-Yandex-API-Key': ADFOX_API_KEY,
           'Content-Type': 'application/json'}

# ===Конфиг отчета===============
date_from = '2023-04-24'
date_to = '2023-06-12'
report_id = '4733'
file_name = r'F:\WORK\AdFox\API_Reports\13.06.2023\custom_report_id{}_{}.xlsx'.\
    format(report_id, datetime.now().strftime("%Y-%m-%d-%H%M%S"))
# ===Конец конфига===============

# получаем список дат для построения отчета
list_date_from = [int(x) for x in date_from.split('-')]
list_date_to = [int(x) for x in date_to.split('-')]
dt_date_from = datetime(list_date_from[0], list_date_from[1], list_date_from[2])
dt_date_to = datetime(list_date_to[0], list_date_to[1], list_date_to[2])

delta = dt_date_to - dt_date_from

date_list = [dt_date_from + timedelta(days=x) for x in range(delta.days + 1)]

task_url = 'https://adfox.yandex.ru/api/report/owner'

report_data_list = []

for day in date_list:
    task_date_to = f'{day.year}-{day.month:02}-{day.day:02}'
    print(task_date_to)
    params = (
        ('name', 'custom_' + report_id),
        ('dateFrom', date_from),
        ('dateTo', task_date_to)
    )
    task_response = requests.get(task_url, params=params, headers=headers)
    task_id = task_response.json()['result']['taskId']

    report_url = "https://adfox.yandex.ru/api/report/result?taskId=" + task_id
    report_params = ('taskId', task_id)

    report_response = requests.get(report_url, headers=headers)
    impressions = report_response.json()['result']['table'][0][1]
    uniq_impressions = report_response.json()['result']['table'][0][2]
    frequency = round(impressions / uniq_impressions, 2)

    report_str = [task_date_to,
                  impressions,
                  uniq_impressions,
                  frequency]

    report_data_list.append(report_str)


report_df = pd.DataFrame(data=report_data_list, columns=['День', 'Показы Нарастающим итогом',
                                                         'Охват нарастающим итогом', 'Частота нарастающим итогом'])

with pd.ExcelWriter(file_name, engine="xlsxwriter") as writer:
    report_df.to_excel(writer, sheet_name='Report', startrow=6, startcol=0, index=False)
    worksheet = writer.sheets['Report']

    worksheet.write(0, 0, 'Название отчета:')
    worksheet.write(0, 1, 'Охват нарастающим итогом по группе суперкампаний')
    worksheet.write(1, 0, 'Date from:')
    worksheet.write(1, 1, date_from)
    worksheet.write(2, 0, 'Date to:')
    worksheet.write(2, 1, date_to)
    worksheet.write(3, 0, 'ID Суперкампаний:')
    worksheet.write(3, 1, '223162,224092,226132')  # Скопировать из настроек сохраненного отчета
