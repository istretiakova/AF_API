# -*- coding: utf-8 -*-
"""
Created on Mon Jun 22 18:56:11 2020

@author: Irina Tretiakova

Получаем данные о настройках размещения (placement) для списка кампаний

"""

import pandas as pd
import xmltodict
import requests
from datetime import datetime
from settings_gpmd import ADFOX_API_KEY

headers = {'X-Yandex-API-Key': ADFOX_API_KEY}
url = 'https://adfox.yandex.ru/api/v1'

campaigns_file = r'F:\WORK\AdFox\API_Reports\11.07.2022\campaigns.csv'
# Требования к файлу:
#     - должен содержать ID кампаний в поле 'ID кампании'
#     - должен содержать Название кампании в поле 'Название кампании'
#     - не должно быть строк с ID кампании = 0 или пустым, и Тестовых кампаний

campaigns_list = pd.read_csv(campaigns_file, sep=';', encoding='utf8')
campaigns_num = campaigns_list.shape[0]
n = 0

data_header = 'bannerID\tbannerName\tsiteID\tsiteName\tzoneID\tzoneName\tcampaignID\tcampaignName\r'

file_name = r'F:\WORK\AdFox\API_Reports\11.07.2022\campaigns_short_placement_{}.tsv'.format(
    datetime.now().strftime("%Y-%m-%d-%H%M%S"))

with open(file_name, mode='w', encoding='cp1251') as file:
    file.write(data_header)

print(f'Всего кампаний {campaigns_num}')

for index, campaign in campaigns_list.iterrows():
    campaign_id = campaign['ID кампании']
    campaign_name = campaign['Название кампании']
    print(f'кампания {n} из {campaigns_num} -> ID кампании {campaign_id}')
    n += 1
    limit = 1000
    offset = 0
    page = 0
    total_pages = 1

    while page < total_pages:
        params = (
            ('object', 'campaign'),
            ('action', 'info'),
            ('actionObject', 'placement'),
            ('objectID', campaign_id),
            ('offset', offset),
            ('limit', limit),
            ('encoding', 'UTF-8')
        )

        response = requests.get(url, params=params, headers=headers)
        response_dict = xmltodict.parse(response.text)

        total_pages = response_dict['response']['result']['total_pages']
        page = response_dict['response']['result']['page']
        offset += 1000

        data = response_dict['response']['result']['data']

        campaign_placement_df = pd.DataFrame.from_dict(data).transpose().reset_index()

        campaign_placement_short = campaign_placement_df[['bannerID', 'bannerName', 'siteID', 'siteName',
                                                          'zoneID', 'zoneName']].drop_duplicates()

        campaign_placement_short['campaignID'] = campaign_id
        campaign_placement_short['campaignName'] = campaign_name

        campaign_placement_short.to_csv(file_name, mode='a', header=False,
                                        sep='\t', encoding='cp1251', index=False)

print('Отчет готов и находится здесь: {}'.format(file_name))
