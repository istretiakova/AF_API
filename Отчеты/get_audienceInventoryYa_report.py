# -*- coding: utf-8 -*-
"""
Created on Fri Jun 26 12:19:26 2020

@author: Irina Tretiakova

Получение отчета по трафику сегментов Я.Аудиторий для списка сайтов

"""

import requests
import pandas as pd
from datetime import datetime
import time


def get_sites_report(key, date_from, date_to):
    ''''
    Получаем отчет по сайтам за период с dateFrom по dateTo и выводим результат в pandas.DataFrame
    
    '''

    sites_report_data = pd.DataFrame({'result':[None]}, index=['state'])
    
    task_url = 'https://adfox.yandex.ru/api/report/owner'
        
    params = (
        ('name', 'sites'),
        ('dateFrom', date_from),
        ('dateTo', date_to)
    )
    
    headers = {
        'X-Yandex-API-Key': key,
        'Content-Type': 'application/json'
    }
    
    sites_task_response = requests.get(task_url, params=params, headers=headers)
    
    sites_report_url = 'https://adfox.yandex.ru/api/report/result?taskId=' +\
        pd.DataFrame(sites_task_response.json())['result']['taskId']
        
    while sites_report_data.loc['state', 'result'] != 'SUCCESS':
            sites_report_url = 'https://adfox.yandex.ru/api/report/result?taskId=' + pd.DataFrame(sites_task_response.json())['result']['taskId']
            sites_report_response = requests.get(sites_report_url, headers=headers)
            sites_report_data = pd.DataFrame(sites_report_response.json())
            time.sleep(2)
        
    sites_report_response = requests.get(sites_report_url, headers=headers)
    sites_report_data = pd.DataFrame(sites_report_response.json())
    sites_report_table = pd.DataFrame(sites_report_data.loc['table', 'result'], columns=sites_report_data.loc['fields', 'result'])
    print('sites_report_table - SUCCESS')
    return sites_report_table


def get_audienceInventoryYa_by_site_report(key, date_from, date_to, sites_list):
    ''''
    Получаем отчет по разделам сайтов из списка sites_list за период с dateFrom по dateTo и выводим результат в pandas.DataFrame

    '''
    audienceInventoryYa_by_site_report_table = pd.DataFrame()
    audienceInventoryYa_by_site_headers = {
        'X-Yandex-API-Key': key,
        'Content-Type': 'application/json'
    }
    
    for site_id in sites_list.index:
        site_name = sites_list.loc[site_id]['siteName']
        audienceInventoryYa_by_site_report_data = pd.DataFrame({'result':[None]}, index=['state'])
        print('siteId = {}; siteName = {}'.format(site_id, site_name))
        audienceInventoryYa_by_site_params = (
            ('name', 'audienceInventoryYa'),
            ('siteId', site_id),
            ('dateFrom', date_from),
            ('dateTo', date_to)
        )

        audienceInventoryYa_by_site_task_response = requests.get('https://adfox.yandex.ru/api/report/site', params = audienceInventoryYa_by_site_params, headers = audienceInventoryYa_by_site_headers)
        print(pd.DataFrame(audienceInventoryYa_by_site_task_response.json())['result']['taskId'])
        while audienceInventoryYa_by_site_report_data.loc['state', 'result'] != 'SUCCESS':
            audienceInventoryYa_by_site_report_url = 'https://adfox.yandex.ru/api/report/result?taskId=' + pd.DataFrame(audienceInventoryYa_by_site_task_response.json())['result']['taskId']
            audienceInventoryYa_by_site_report_response = requests.get(audienceInventoryYa_by_site_report_url, headers=audienceInventoryYa_by_site_headers)
            audienceInventoryYa_by_site_report_data = pd.DataFrame(audienceInventoryYa_by_site_report_response.json())
            time.sleep(2)
            print(audienceInventoryYa_by_site_report_data.loc['state', 'result'])
        audienceInventoryYa_by_site_report_table_chunk = pd.DataFrame(audienceInventoryYa_by_site_report_data.loc['table', 'result'], columns=audienceInventoryYa_by_site_report_data.loc['fields', 'result'])
        audienceInventoryYa_by_site_report_table_chunk['siteId'] = site_id
        audienceInventoryYa_by_site_report_table_chunk['siteName'] = site_name
        audienceInventoryYa_by_site_report_table = pd.concat([audienceInventoryYa_by_site_report_table, audienceInventoryYa_by_site_report_table_chunk], ignore_index=True)
    print('audienceInventoryYa_by_site_report_table - SUCCESS')
    return audienceInventoryYa_by_site_report_table


def get_socdemSexesAgesLoadsTotal_by_site_report(key, date_from, date_to, sites_list):
    ''''
    Получаем отчет по разделам сайтов из списка sites_list за период с dateFrom по dateTo и выводим результат в pandas.DataFrame

    '''
    socdemSexesAgesLoadsTotal_by_site_report_table = pd.DataFrame()
    socdemSexesAgesLoadsTotal_by_site_headers = {
        'X-Yandex-API-Key': key,
        'Content-Type': 'application/json'
    }
    
    for site_id in sites_list.index:
        site_name = sites_list.loc[site_id]['siteName']
        socdemSexesAgesLoadsTotal_by_site_report_data = pd.DataFrame({'result':[None]}, index=['state'])
        print('siteId = {}; siteName = {}'.format(site_id, site_name))
        socdemSexesAgesLoadsTotal_by_site_params = (
            ('name', 'socdemSexesAgesLoadsTotal'),
            ('siteId', site_id),
            ('dateFrom', date_from),
            ('dateTo', date_to)
        )

        socdemSexesAgesLoadsTotal_by_site_task_response = requests.get('https://adfox.yandex.ru/api/report/site', params = socdemSexesAgesLoadsTotal_by_site_params, headers = socdemSexesAgesLoadsTotal_by_site_headers)
        print(pd.DataFrame(socdemSexesAgesLoadsTotal_by_site_task_response.json())['result']['taskId'])
        while socdemSexesAgesLoadsTotal_by_site_report_data.loc['state', 'result'] != 'SUCCESS':
            socdemSexesAgesLoadsTotal_by_site_report_url = 'https://adfox.yandex.ru/api/report/result?taskId=' + pd.DataFrame(socdemSexesAgesLoadsTotal_by_site_task_response.json())['result']['taskId']
            socdemSexesAgesLoadsTotal_by_site_report_response = requests.get(socdemSexesAgesLoadsTotal_by_site_report_url, headers=socdemSexesAgesLoadsTotal_by_site_headers)
            socdemSexesAgesLoadsTotal_by_site_report_data = pd.DataFrame(socdemSexesAgesLoadsTotal_by_site_report_response.json())
            time.sleep(0.5)
            print(socdemSexesAgesLoadsTotal_by_site_report_data.loc['state', 'result'])
        socdemSexesAgesLoadsTotal_by_site_report_table_chunk = pd.DataFrame(socdemSexesAgesLoadsTotal_by_site_report_data.loc['table', 'result'], columns=socdemSexesAgesLoadsTotal_by_site_report_data.loc['fields', 'result'])
        socdemSexesAgesLoadsTotal_by_site_report_table_chunk['siteId'] = site_id
        socdemSexesAgesLoadsTotal_by_site_report_table_chunk['siteName'] = site_name
        socdemSexesAgesLoadsTotal_by_site_report_table = pd.concat([socdemSexesAgesLoadsTotal_by_site_report_table, socdemSexesAgesLoadsTotal_by_site_report_table_chunk], ignore_index=True)
    print('socdemSexesAgesLoadsTotal_by_site_report_table - SUCCESS')
    return socdemSexesAgesLoadsTotal_by_site_report_table



key = '4963dde8-b933-47b0-9854-e3a01ea5ebac'
date_from = '2021-05-01'
date_to = '2020-05-31'
loads_total = 1000

# Получаем отчет по сайтам за активный период
sites_report_table = get_sites_report(key, date_from, date_to)    
# Определяем список сайтов, активных в активном периоде
active_sites = sites_report_table.loc[lambda sites_report_data: sites_report_data['loadsTotal']>loads_total, ['siteId', 'siteName']].set_index('siteId')
# Для активных сайтов получаем отчет по трафику сегментов Я.Аудиторий
# audienceInventoryYa_by_site_report_table = get_audienceInventoryYa_by_site_report(key, date_from, date_to, active_sites)
# Для активных сайтов получаем отчет по запросам по полу и возрасту
socdemSexesAgesLoadsTotal_by_site_report_table = get_socdemSexesAgesLoadsTotal_by_site_report(key, date_from, date_to, active_sites)


file_name = r'C:\Users\Natalia\Downloads\VN_socdem_by_site_may2020_{}.xlsx'.format(datetime.now().strftime("%Y-%m-%d-%H%M%S"))

with pd.ExcelWriter(file_name) as writer:
    # audienceInventoryYa_by_site_report_table.to_excel(writer, sheet_name='audienceInventoryYa_report')
    socdemSexesAgesLoadsTotal_by_site_report_table.to_excel(writer, sheet_name='socdemSexesAgesLoadsTotal')
    sites_report_table.to_excel(writer, sheet_name='sites_report')
    active_sites.to_excel(writer, sheet_name='active_sites')
    
print('Отчет готов и находится здесь: {}'.format(file_name))
