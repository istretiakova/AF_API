# -*- coding: utf-8 -*-
"""
Created on Mon Jul 13 17:31:26 2020

@author: Irina Tretiakova

Конвертируем справочник площадок, полученный по API от Adfox в таблицу Excel

"""

import pandas as pd
import xml.etree.ElementTree as ET
import requests
from datetime import datetime
from settings import ADFOX_API_KEY

# ===== Начало конфига параметров отчета =====
# ID сайта AdFox для фильтра. Если нужны все площадки, то оставить пустым: site_id = ''
site_id = ''

# Название файла с выгрузкой
file_name = r'F:\WORK\AdFox\Справочники\DA_AF_Tags_siteID_{}_{}.xlsx'.format(site_id,
                                                                             datetime.now().strftime("%Y-%m-%d-%H%M%S"))
# ===== Конец конфига параметров отчета =====

a_lowercase = ord('a')
alfabet_size = 26


def _decompose(number):
    """Generate digits from `number` in base alphabet, least significants
    bits first.

    Since A is 1 rather than 0 in base alphabet, we are dealing with
    `number - 1` at each iteration to be able to extract the proper digits.
    """

    while number:
        number, remainder = divmod(number, alfabet_size)
        yield remainder


def base_10_to_alphabet(number):
    """Convert a decimal number to its base alphabet representation"""

    return ''.join(
        chr(a_lowercase + part)
        for part in _decompose(number)
    )[::-1]


headers = {'X-Yandex-API-Key': ADFOX_API_KEY}
url = 'https://adfox.yandex.ru/api/v1'

limit = 1000
offset = 0

total_rows = limit + 1
page = 0
rows = 0

writer = pd.ExcelWriter(file_name, engine='xlsxwriter', options={'strings_to_urls': False})

with writer:
    while rows + (page - 1) * limit < total_rows:
        print('Данные страницы {} запрошены и обрабатываются'.format(page + 1))

        params = (
            ('object', 'account'),
            ('action', 'list'),
            ('actionObject', 'place'),
            ('actionObjectID2', site_id),
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
        places_info_rows = []

        for row in data:
            place_data = {}
            for child in list(row):
                try:
                    value = int(child.text)
                except:
                    value = child.text
                place_data[child.tag] = value
            p1 = base_10_to_alphabet(int(row.find("ID").text)) if row.find("ID").text is not None else 0
            place_data['p1 (ID base26)'] = p1
            p2 = base_10_to_alphabet(int(row.find("bannerTypeID").text)) if row.find("bannerTypeID"). \
                                                                                text is not None else 0
            place_data['p2 (bannerTypeID base26)'] = p2
            place_data['DA AdFox base Tag'] = f"https://yandex.ru/ads/adfox/226279/getCode?p1={p1}&p2={p2}"
            places_info_rows.append(place_data)

        places_info_list = pd.DataFrame(places_info_rows)
        places_short_info_list = places_info_list[['siteID', 'siteName', 'zoneID', 'zoneName', 'ID', 'name',
                                                   'bannerTypeName', 'p1 (ID base26)', 'p2 (bannerTypeID base26)',
                                                   'DA AdFox base Tag']]
        places_short_info_list = places_short_info_list.rename(columns={'p1 (ID base26)': 'p1',
                                                                        'p2 (bannerTypeID base26)': 'p2',
                                                                        'zoneID': 'sectionID',
                                                                        'zoneName': 'sectionName',
                                                                        'ID': 'placeID',
                                                                        'name': 'placeName'})
        places_short_info_list['DA AdFox extra parameters'] = '&puid1=[[PUID1_VALUE]]&puid5=[[PUID5_VALUE]]' \
                                                           '&puid6=[[PUID6_VALUE]]&puid8=[[PUID8_VALUE]]' \
                                                           '&puid9=[[PUID9_VALUE]]&extid=[[EXTID_VALUE]]' \
                                                           '&extid_tag=[[EXTID_TAG_VALUE]]&pr=[[PR_VALUE]]' \
                                                           '&eid1=[[EID1_VALUE]]&idfa=[[IDFA]]&google_aid=[[GAID]]' \
                                                           '&ext_duid=[[EXT_DUID_VALUE]]&eid3=[[EID3_VALUE]]' \
                                                           '&dl=[[PAGE_URL]]'

        if page == 1:
            print('total_pages = {}'.format(total_pages))
            print('total_rows = {}'.format(total_rows))
            places_short_info_list.to_excel(writer, sheet_name='DA_AdFox_Tags', index=False)
        else:
            places_short_info_list.to_excel(writer, sheet_name='DA_AdFox_Tags', startrow=offset + 1, header=False,
                                            index=False)

        offset += limit

    for column in places_short_info_list:
        column_width = max(places_short_info_list[column].astype(str).map(len).max(), len(column))
        col_idx = places_short_info_list.columns.get_loc(column)
        writer.sheets['DA_AdFox_Tags'].set_column(col_idx, col_idx, column_width)

    col_idx = places_short_info_list.columns.get_loc('DA AdFox extra parameters')
    writer.sheets['DA_AdFox_Tags'].set_column(col_idx, col_idx, 60)

print('Отчет готов и находится здесь: {}'.format(file_name))
