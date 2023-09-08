import pandas as pd
import xml.etree.ElementTree as ET
import requests
from datetime import datetime

from settings import TOKEN

headers = {'Authorization': 'OAuth ' + TOKEN}
url = 'https://adfox.yandex.ru/api/v1'

file_name = r'F:\WORK\_PBI\Videonet_Monitoring_data\Catalogs\advertisers_list_{}.xlsx'.\
    format(datetime.now().strftime("%Y-%m-%d-%H%M%S"))

limit = 1000
offset = 0

total_rows = limit + 1
page = 0
rows = 0

fields = {'ID': 'Advertiser ID',
          'account': 'Advertiser account',
          'company': 'Advertiser company'}

advertisers_info_rows = []

while rows + (page - 1) * limit < total_rows:
    print('Данные страницы {} запрошены и обрабатываются'.format(page + 1))

    params = (
        ('object', 'account'),
        ('action', 'list'),
        ('actionObject', 'advertiser'),
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
        advertiser_data = {}
        for child in list(row):
            if child.tag in fields:
                field_name = fields[child.tag]
                value = child.text
                advertiser_data[field_name] = value
        advertisers_info_rows.append(advertiser_data)

    offset += limit

advertisers_info_list = pd.DataFrame(advertisers_info_rows)

# print(advertisers_info_list)
advertisers_info_list.to_excel(file_name)
