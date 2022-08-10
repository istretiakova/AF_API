# -*- coding: utf-8 -*-
"""
Created on Tue Jun  9 17:19:53 2020

@author: Irina Tretiakova

Получаем списко активных разделов сайтов Adfox

"""

import requests
import pandas as pd
from datetime import datetime
import time
import xml.etree.ElementTree as ET

key = '5313a9e4-5ab7-4742-b292-39602532534f'
date_from = '2020-09-01'
date_to = '2020-09-29'


def get_sites_report(key, date_from, date_to):
    """
    Получаем отчет по сайтам за период с dateFrom по dateTo и выводим результат в pandas.DataFrame

    """

    sites_report_data = pd.DataFrame({'result': [None]}, index=['state'])

    sites_task_url = 'https://adfox.yandex.ru/api/report/owner'

    params = (
        ('name', 'sites'),
        ('dateFrom', date_from),
        ('dateTo', date_to)
    )

    headers = {
        'X-Yandex-API-Key': key,
        'Content-Type': 'application/json'
    }
    print('Запрашиваем отчет по сайтам...')
    sites_task_response = requests.get(sites_task_url, params=params, headers=headers)

    sites_report_url = 'https://adfox.yandex.ru/api/report/result?taskId=' + \
                       pd.DataFrame(sites_task_response.json())['result']['taskId']

    while sites_report_data.loc['state', 'result'] != 'SUCCESS':
        sites_report_url = 'https://adfox.yandex.ru/api/report/result?taskId=' + \
                           pd.DataFrame(sites_task_response.json())['result']['taskId']
        sites_report_response = requests.get(sites_report_url, headers=headers)
        sites_report_data = pd.DataFrame(sites_report_response.json())
        time.sleep(2)

    sites_report_response = requests.get(sites_report_url, headers=headers)
    sites_report_data = pd.DataFrame(sites_report_response.json())
    sites_report_table = pd.DataFrame(sites_report_data.loc['table', 'result'],
                                      columns=sites_report_data.loc['fields', 'result'])
    print('sites_report_table - SUCCESS')
    return sites_report_table


def get_sections_report(key, date_from, date_to, sites_list):
    """
    Получаем отчет по разделам сайтов из списка sites_list за период с dateFrom по dateTo
    и выводим результат в pandas.DataFrame

    """
    section_report_table = pd.DataFrame()
    sections_headers = {
        'X-Yandex-API-Key': key,
        'Content-Type': 'application/json'
    }
    print('Запрашиваем отчеты по разделам...')
    for site_id in sites_list.index:
        site_name = sites_list.loc[site_id]['siteName']
        section_report_data = pd.DataFrame({'result': [None]}, index=['state'])
        # print('siteId = {}; siteName = {}'.format(site_id, site_name))
        sections_params = (
            ('name', 'sections'),
            ('siteId', site_id),
            ('dateFrom', date_from),
            ('dateTo', date_to)
        )

        section_task_response = requests.get('https://adfox.yandex.ru/api/report/site', params=sections_params,
                                             headers=sections_headers)
        # print(pd.DataFrame(section_task_response.json())['result']['taskId'])
        while section_report_data.loc['state', 'result'] != 'SUCCESS':
            section_report_url = 'https://adfox.yandex.ru/api/report/result?taskId=' + \
                                 pd.DataFrame(section_task_response.json())['result']['taskId']
            section_report_response = requests.get(section_report_url, headers=sections_headers)
            section_report_data = pd.DataFrame(section_report_response.json())
            time.sleep(2)
            # print(section_report_data.loc['state', 'result'])
        section_report_table_chunk = pd.DataFrame(section_report_data.loc['table', 'result'],
                                                  columns=section_report_data.loc['fields', 'result'])
        section_report_table_chunk['siteId'] = site_id
        section_report_table_chunk['siteName'] = site_name
        section_report_table = pd.concat([section_report_table, section_report_table_chunk], ignore_index=True)
    print('section_report_table - SUCCESS')
    return section_report_table


def get_places_report(key, date_from, date_to, sections_list):
    """
    Получаем отчет по площадкам активных разделов сайтов из списка sections_list за период с dateFrom по dateTo и выводим результат в pandas.DataFrame

    """
    places_report_table = pd.DataFrame()
    places_headers = {
        'X-Yandex-API-Key': key,
        'Content-Type': 'application/json'
    }
    print('Запрашиваем отчеты по площадкам...')
    for section_id in sections_list.index:
        section_name = sections_list.loc[section_id]['sectionName']
        site_id = sections_list.loc[section_id]['siteId']
        site_name = sections_list.loc[section_id]['siteName']
        places_report_data = pd.DataFrame({'result': [None]}, index=['state'])
        places_params = (
            ('name', 'places'),
            ('sectionId', section_id),
            ('dateFrom', date_from),
            ('dateTo', date_to)
        )

        places_task_response = requests.get('https://adfox.yandex.ru/api/report/section', params=places_params,
                                            headers=places_headers)
        # print(pd.DataFrame(places_task_response.json())['result']['taskId'])
        while places_report_data.loc['state', 'result'] != 'SUCCESS':
            places_report_url = 'https://adfox.yandex.ru/api/report/result?taskId=' + \
                                pd.DataFrame(places_task_response.json())['result']['taskId']
            places_report_response = requests.get(places_report_url, headers=places_headers)
            places_report_data = pd.DataFrame(places_report_response.json())
            # print(places_report_data.loc['state', 'result'])
            time.sleep(2)
        places_report_table_chunk = pd.DataFrame(places_report_data.loc['table', 'result'],
                                                 columns=places_report_data.loc['fields', 'result'])
        places_report_table_chunk['sectionId'] = section_id
        places_report_table_chunk['sectionName'] = section_name
        places_report_table_chunk['siteId'] = site_id
        places_report_table_chunk['siteName'] = site_name
        places_report_table = pd.concat([places_report_table, places_report_table_chunk], ignore_index=True)
    print('places_report_table - SUCCESS')
    return places_report_table


def get_default_banners_info(key, listPlaceIDs):
    """
    Получаем данные о дефолтных баннерах по списку площадок

    """
    url = 'https://adfox.yandex.ru/api/v1'

    headers = {
        'X-Yandex-API-Key': key,
        'Content-Type': 'application/json'
    }

    offset = 0
    limit = 1000

    params = (
        ('object', 'account'),
        ('action', 'list'),
        ('actionObject', 'defaultBanner'),
        ('listPlaceIDs', listPlaceIDs),
        ('offset', offset),
        ('limit', limit),
        ('encoding', 'UTF-8')
    )
    total_rows = limit + 1
    page = 0
    rows = 0
    default_banners_info_rows = []
    print('Запрашиваем инфо о дефолтных баннерах...')
    while rows + (page - 1) * limit < total_rows:
        print('Данные страницы {} запрошены и обрабатываются'.format(page + 1))

        params = (
            ('object', 'account'),
            ('action', 'list'),
            ('actionObject', 'defaultBanner'),
            ('listPlaceIDs', listPlaceIDs),
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

        for row in data:
            default_banner_data = {}
            for child in list(row):
                try:
                    value = int(child.text)
                except:
                    value = child.text
                default_banner_data[child.tag] = value
            default_banners_info_rows.append(default_banner_data)

        offset += limit

    default_banners_info_list = pd.DataFrame(default_banners_info_rows)
    return default_banners_info_list


loads_total = 1000
# Получаем отчет по сайтам за активный период
sites_report_table = get_sites_report(key, date_from, date_to)
# Определяем список сайтов, активных в активном периоде
active_sites = sites_report_table.loc[
    lambda sites_report_data: sites_report_data['loadsTotal'] > loads_total, ['siteId', 'siteName']].set_index('siteId')

# active_sites = sites_report_table.loc[['siteId', 'siteName']].set_index('siteId')

# Для активных сайтов получаем отчет по разделам за активный период
sections_report_table = get_sections_report(key, date_from, date_to, active_sites)
# Определяем список активных разделов
active_sections = sections_report_table.loc[
    lambda sections_report_data: sections_report_data['loadsTotal'] > loads_total, ['sectionId', 'sectionName',
                                                                                    'siteId', 'siteName']].set_index(
    'sectionId')

# active_sections = sections_report_table[['sectionId', 'sectionName', 'siteId', 'siteName']].set_index('sectionId')

# Для активных разделов получаем отчет по площадкам за активный период
places_report_table = get_places_report(key, date_from, date_to, active_sections)
# Выбираем площадки, активные в данном периоде
active_places = places_report_table.loc[
    lambda places_report_data: places_report_data['loadsTotal'] > loads_total, ['placeId', 'placeName', 'sectionId',
                                                                                'sectionName', 'siteId',
                                                                                'siteName']].set_index('placeId')

# active_places = places_report_table[['placeId', 'placeName', 'sectionId', 'sectionName', 'siteId', 'siteName']].set_index('placeId')

# Формируем список ID активных площадок в виде строки
listPlaceIDs = str(active_places.index.to_list())[1:-1].replace(" ", "")
# Получаем инфо о дефолтных баннерах дл яактивных площадок
default_banners_info_list = get_default_banners_info(key, listPlaceIDs)

file_name = r'C:\Users\Natalia\Downloads\IMN_inventory_report_{}-{}_{}.xlsx'.format(date_from, date_to,
    datetime.now().strftime("%Y-%m-%d-%H%M%S"))

with pd.ExcelWriter(file_name) as writer:
    sections_report_table.to_excel(writer, sheet_name='section_report')
    sites_report_table.to_excel(writer, sheet_name='sites_report')
    active_sites.to_excel(writer, sheet_name='active_sites')
    active_sections.to_excel(writer, sheet_name='active_sections')
    places_report_table.to_excel(writer, sheet_name='places_report')
    active_places.to_excel(writer, sheet_name='active_places')
    default_banners_info_list.to_excel(writer, sheet_name='default_banners')

print('Отчет готов и находится здесь: {}'.format(file_name))
