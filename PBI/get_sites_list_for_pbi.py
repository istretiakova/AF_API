import pandas as pd
import xml.etree.ElementTree as ET
import requests
from datetime import datetime

from settings import TOKEN

headers = {'Authorization': 'OAuth ' + TOKEN}
url = 'https://adfox.yandex.ru/api/v1'

file_name = r'F:\WORK\_PBI\Videonet_Monitoring_data\Catalogs\sites_list_{}.xlsx'.\
    format(datetime.now().strftime("%Y-%m-%d-%H%M%S"))

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

# print(sites_info_list)
sites_info_list.to_excel(file_name)
