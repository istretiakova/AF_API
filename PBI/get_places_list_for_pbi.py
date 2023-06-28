import pandas as pd
import xml.etree.ElementTree as ET
import requests

from settings import ADFOX_API_KEY

headers = {'X-Yandex-API-Key': ADFOX_API_KEY}
url = 'https://adfox.yandex.ru/api/v1'

limit = 1000
offset = 0

total_rows = limit + 1
page = 0
rows = 0

fields = {'ID': 'Place ID',
          'name': 'Place name',
          'zoneID': 'Section ID',
          'zoneName': 'Section Name',
          'siteID': 'Site ID',
          'siteName': 'Site name',
          'bannerTypeName': 'Banner Type'}

places_info_rows = []

while rows + (page - 1) * limit < total_rows:
    print('Данные страницы {} запрошены и обрабатываются'.format(page + 1))

    params = (
        ('object', 'account'),
        ('action', 'list'),
        ('actionObject', 'place'),
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
        place_data = {}
        for child in list(row):
            if child.tag in fields:
                field_name = fields[child.tag]
                value = child.text
                place_data[field_name] = value
        places_info_rows.append(place_data)

    offset += limit

places_list = pd.DataFrame(places_info_rows)

print(places_list)
