# -*- coding: utf-8 -*-
"""
Created on Mon Jul 13 18:00:22 2020

@author: Irina Tretiakova

Конвертируем справочник сайтов, полученный по API от Adfox в таблицу Excel

"""

import pandas as pd
import xml.etree.ElementTree as ET
import requests
from datetime import datetime
from settings import ADFOX_API_KEY

a_lowercase = ord('a')
alphabet_size = 26


def _decompose(number):
    """Generate digits from `number` in base alphabet, least significants
    bits first.

    Since A is 1 rather than 0 in base alphabet, we are dealing with
    `number - 1` at each iteration to be able to extract the proper digits.
    """

    while number:
        number, remainder = divmod(number, alphabet_size)
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

file_name = r'F:\WORK\AdFox\Справочники\DA_sites_info_{}.xlsx'.format(datetime.now().strftime("%Y-%m-%d-%H%M%S"))

writer = pd.ExcelWriter(file_name)

with writer:
    while rows + (page - 1) * limit < total_rows:
        print('Данные страницы {} запрошены и обрабатываются'.format(page + 1))

        params = (
            ('object', 'account'),
            ('action', 'list'),
            ('actionObject', 'website'),
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
        sites_info_rows = []

        for row in data:
            site_data = {}
            for child in list(row):
                try:
                    value = int(child.text)
                except:
                    value = child.text
                site_data[child.tag] = value

            if row.find("name").text.lower().find('archive') >= 0 \
                    or row.find("name").text.lower().find('old') >= 0 \
                    or row.find("name").text.lower().find('архив') >= 0:
                s_type = 'archive'
            elif row.find("name").text.lower().find('smart') >= 0 \
                    or row.find("name").text.lower().find('iptv') >= 0 \
                    or row.find("name").text.lower().find('connected tv') >= 0:
                s_type = 'smart TV app'
            elif row.find("name").text.lower().find('(bn)') >= 0:
                if row.find("name").text.lower().find('(mobile)') >= 0:
                    s_type = 'BN mobile'
                else:
                    s_type = 'BN'
            elif row.find("name").text.lower().find('(mn)') >= 0:
                s_type = 'MN'
            elif row.find("name").text.lower().find('(mobile)') >= 0 or row.find("name").text.lower().find(
                    '(vitrinatv) mobile') >= 0:
                s_type = 'mobile app'
            elif row.find("name").text.lower().find('roll') >= 0 or row.find("name").text.lower().find(
                    'outstream') >= 0:
                s_type = 'outstream web'
            elif row.find("webmasterAccount").text is None \
                    or row.find("webmasterAccount").text.lower().find('test') >= 0 \
                    or row.find("name").text.lower().find('test') >= 0 \
                    or row.find("name").text.lower().find('тест') >= 0:
                s_type = 'test'
            else:
                s_type = 'instream web'

            site_data['base26'] = base_10_to_alphabet(int(row.find("ID").text))
            site_data['site type'] = s_type

            sites_info_rows.append(site_data)

        sites_info_list = pd.DataFrame(sites_info_rows)
        sites_short_info_list = sites_info_list[
            ['ID', 'name', 'webmasterID', 'webmasterAccount', 'base26', 'site type']]

        if page == 1:
            print('total_pages = {}'.format(total_pages))
            print('total_rows = {}'.format(total_rows))
            sites_short_info_list.to_excel(writer, sheet_name='short_data', index=False)
            sites_info_list.to_excel(writer, sheet_name='original_data', index=False)
        else:
            sites_short_info_list.to_excel(writer, sheet_name='short_data', startrow=offset + 1, header=False,
                                           index=False)
            sites_info_list.to_excel(writer, sheet_name='original_data', startrow=offset + 1, header=False, index=False)

        offset += limit

print('Отчет готов и находится здесь: {}'.format(file_name))
