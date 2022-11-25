# -*- coding: utf-8 -*-
"""
Created on Mon Sep 05 18:00:22 2022

@author: Irina Tretiakova

Получаем справочник сайтов AdFox для Admon

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

file_name = r'F:\WORK\AdFox\Справочники\Для Admon и Brain\sections_{}.tsv'\
    .format(datetime.now().strftime("%Y-%m-%d-%H%M%S"))

writer = open(file_name, "w")

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
        sites_info_rows = []

        for row in data:
            site_data = {}
            site_data["ID"] = row.find("ID").text
            site_data["name"] = row.find("name").text
            sites_info_rows.append(site_data)

        sites_info_list = pd.DataFrame(sites_info_rows)

        if page == 1:
            print('total_pages = {}'.format(total_pages))
            print('total_rows = {}'.format(total_rows))
            sites_info_list.to_csv(writer, sep="\t", index=False, encoding="utf8", line_terminator='\n')
        else:
            sites_info_list.to_csv(writer, header=False, index=False, sep="\t",
                                   encoding="utf8", line_terminator='\n')

        offset += limit

print('Отчет готов и находится здесь: {}'.format(file_name))
