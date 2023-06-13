# -*- coding: utf-8 -*-
"""
Created on Tue Aug 25 13:40:05 2020

@author: Irina Tretiakova

Получаем инфо о шаблонах баннеров

"""

import pandas as pd
import xml.etree.ElementTree as ET
import requests
from datetime import datetime
from settings import ADFOX_API_KEY


def get_templates_list(key, banner_type_id):

    headers = {'X-Yandex-API-Key': key}
    url = 'https://adfox.yandex.ru/api/v1'

    limit = 1000
    offset = 0
    params = (
        ('object', 'bannerType'),
        ('action', 'list'),
        ('actionObject', 'template'),
        ('objectID', banner_type_id),
        ('offset', offset),
        ('limit', limit),
        ('encoding', 'UTF-8')
    )

    response = requests.get(url, params=params, headers=headers)
    root = ET.fromstring(response.text)
    data = root.find("result").find("data")
    templates_info_rows = []
    for row in data:
        template_data = {}
        for child in list(row):
            try:
                value = int(child.text)
            except:
                value = child.text
            template_data[child.tag] = value
        templates_info_rows.append(template_data)

    templates_list = pd.DataFrame(templates_info_rows)
    return templates_list


def get_templates_info(key, templates_list, files_url):

    headers = {'X-Yandex-API-Key': key}
    url = 'https://adfox.yandex.ru/api/v1'

    limit = 1000
    offset = 0
    templates_info_rows = []

    for template_id in templates_list['templateID']:
        try:
            params = (
                ('object', 'account'),
                ('action', 'list'),
                ('actionObject', 'template'),
                ('actionObjectID', template_id),
                ('offset', offset),
                ('limit', limit),
                ('encoding', 'UTF-8')
            )

            response = requests.get(url, params=params, headers=headers)
            root = ET.fromstring(response.text)
            data = root.find("result").find("data").find("row0")
            template_data = {'templateID': int(data.find('id').text), 'templateName': data.find('name').text}

            user_parameters = data.find('userParameters')
            for row in user_parameters:
                parameter_id = 'userParameter' + str(row.find('userParameterId').text)
                parameter_name = row.find('name').text
                template_data[parameter_id] = parameter_name

            events = data.find('events')
            for row in events:
                event_id = 'events' + str(row.find('eventId').text)
                event_name = row.find('name').text
                template_data[event_id] = event_name

            template_code = data.find('impressionCode').text
            template_id = template_data['templateID']
            template_name = template_data['templateName'].replace(':', '')

            template_file_name = f"{files_url}\Templates\{template_id}_{template_name}.txt"

            with open(template_file_name, 'w', encoding='utf8') as ff:
                ff.write(template_code)

            templates_info_rows.append(template_data)
        except:
            continue

    templates_info_list = pd.DataFrame(templates_info_rows)
    return templates_info_list


# ==========Конфиг==========

files_url = r'F:\WORK\AdFox\API_Reports\25.10.2022\\'
out_file = f'{files_url}templates_info_{datetime.now().strftime("%Y-%m-%d-%H%M%S")}.xlsx'
banner_type_id = 86755

# =======Конец конфига=======

writer = pd.ExcelWriter(out_file)

templates_list = get_templates_list(ADFOX_API_KEY, banner_type_id)
templates_info_list = get_templates_info(ADFOX_API_KEY, templates_list, files_url)

with writer:
    templates_list.to_excel(writer, sheet_name='templates_list')
    templates_info_list.to_excel(writer, sheet_name='templates_info')

print('Отчет готов и находится здесь: {}'.format(out_file))
