# -*- coding: utf-8 -*-
"""
Created on Fri May 27 12:19:26 2022

@author: Irina Tretiakova

Получение списко отчетов для указанного уровня детализации
"""

import requests
import pandas as pd
from datetime import datetime
import json


key = 'db4e4155-53d9-4db1-a512-ee38a92f6621'
headers = {'X-Yandex-API-Key': key,
           'Content-Type': 'application/json'}

level = 'owner'
# Допустимые варианты для level:
# owner — общий отчет;
# supercampaign — на уровне суперкампании;
# campaign — на уровне кампании;
# banner — на уровне баннера;
# site — на уровне сайта;
# section — на уровне раздела;
# place — на уровне рекламного места.

url = f'https://adfox.yandex.ru/api/report/list/{level}'

response = requests.get(url, headers=headers)

data = json.loads(response.text)
data_df = pd.DataFrame(data["result"]["reports"])

file_name = r'C:\Users\Natalia\Downloads\reports_for_{}_{}.xlsx'.\
    format(level, datetime.now().strftime("%Y-%m-%d-%H%M%S"))
data_df.to_excel(file_name)
print('Отчет готов и находится здесь: {}'.format(file_name))
