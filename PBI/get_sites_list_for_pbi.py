import pandas as pd
import xml.etree.ElementTree as ET
import requests

from settings import ADFOX_API_KEY

headers = {'X-Yandex-API-Key': ADFOX_API_KEY}
url = 'https://adfox.yandex.ru/api/v1'

limit = 1000
offset = 0

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
data = root.find("result").find("data")

sites_info_rows = []
for row in data:
    site_data = {}
    for child in list(row):
        value = child.text
        site_data[child.tag] = value

    sites_info_rows.append(site_data)

sites_info_list = pd.DataFrame(sites_info_rows)[['ID', 'name', 'webmasterAccount']].\
    rename(columns={"ID": "Site ID", "name": "Site name", "webmasterAccount": "Webmaster"})
print(sites_info_list)
