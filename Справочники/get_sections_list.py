# -*- coding: utf-8 -*-
"""
Created on Fri Jul 22 17:31:26 2020

@author: Irina Tretiakova

Конвертируем справочник разделов сайтов, полученный по API от Adfox в таблицу Excel

"""

import pandas as pd
import xml.etree.ElementTree as ET
import requests
from datetime import datetime
from settings import ADFOX_API_KEY


headers = {'X-Yandex-API-Key': ADFOX_API_KEY}
url = 'https://adfox.yandex.ru/api/v1'

limit = 1000
offset = 0

total_rows = limit + 1
page = 0
rows = 0

file_name = r'F:\WORK\AdFox\Справочники\DA_sections_info_{}.xlsx'.format(datetime.now().strftime("%Y-%m-%d-%H%M%S"))

writer = pd.ExcelWriter(file_name)

with writer:
    while rows + (page - 1) * limit < total_rows:
        print('Данные страницы {} запрошены и обрабатываются'.format(page + 1))

        params = (
            ('object', 'account'),
            ('action', 'list'),
            ('actionObject', 'zone'),
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
        sections_info_rows = []

        for row in data:
            section_data = {}
            for child in list(row):
                if child.tag == "template":
                    template = child.find('template1')
                    section_data[template.tag] = template.text
                else:
                    try:
                        value = int(child.text)
                    except:
                        value = child.text
                    section_data[child.tag] = value
            sections_info_rows.append(section_data)

        sections_info_list = pd.DataFrame(sections_info_rows)
        if page == 1:
            print('total_pages = {}'.format(total_pages))
            print('total_rows = {}'.format(total_rows))
            sections_info_list.to_excel(writer, sheet_name='data', index=False)
        else:
            sections_info_list.to_excel(writer, sheet_name='data', startrow=offset + 1, header=False, index=False)

        offset += limit

print('Отчет готов и находится здесь: {}'.format(file_name))
