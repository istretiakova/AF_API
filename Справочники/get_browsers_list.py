# -*- coding: utf-8 -*-
"""
Created on Fri Feb 03 13:40:05 2020

@author: Irina Tretiakova

Получаем справочник браузеров

"""

import pandas as pd
import xml.etree.ElementTree as ET
import requests
from datetime import datetime
from settings import ADFOX_API_KEY


headers = {'X-Yandex-API-Key': ADFOX_API_KEY}
url = 'https://adfox.yandex.ru/api/v1'

file_name = r'F:\WORK\AdFox\Справочники\DA_browsers_list_{}.xlsx'.format(datetime.now().strftime("%Y-%m-%d-%H%M%S"))

writer = pd.ExcelWriter(file_name)

with writer:
    params = (
        ('object', 'account'),
        ('action', 'utility'),
        ('actionObject', 'browser')
    )

    response = requests.get(url, params=params, headers=headers)
    root = ET.fromstring(response.text)

    data = root.find("result").find("data")
    browser_info_rows = []

    for row in data:
        browser_data = {}
        for child in list(row):
            try:
                value = int(child.text)
            except:
                value = child.text
            browser_data[child.tag] = value
        browser_info_rows.append(browser_data)

    browser_info_list = pd.DataFrame(browser_info_rows)
    browser_info_list.to_excel(writer, index=False)

print('Отчет готов и находится здесь: {}'.format(file_name))
