# -*- coding: utf-8 -*-
"""
Created on Wen Sep 22 18:56:11 2021

@author: Irina Tretiakova

Получаем информацию о кампаниях из списка кампаний (даты старта и финиша и плановый объем показов)

"""

import pandas as pd
import xml.etree.ElementTree as ET
import requests
from datetime import datetime
from settings import TOKEN

headers = {'Authorization': 'OAuth ' + TOKEN}
url = 'https://adfox.yandex.ru/api/v1'

campaigns_list = pd.read_csv(r'F:\WORK\AdFox\API_Reports\10.01.2024\campaigns.csv',
                             sep=';', encoding='utf8')
n = 1

campaigns_info_rows = []
campaigns_num = campaigns_list.shape[0]
for campaign_id in campaigns_list['ID кампании']:
    print(f'{n} -> {campaign_id} из {campaigns_num}')
    n += 1
    params = (
        ('object', 'account'),
        ('action', 'list'),
        ('actionObject', 'campaign'),
        ('actionObjectID', campaign_id),
        ('offset', '0'),
        ('limit', '1000'),
        ('encoding', 'UTF-8')
    )

    response = requests.get(url, params=params, headers=headers)
    root = ET.fromstring(response.text)
    data = root.find("result").find("data").find("row0")

    campaign_data = {
        "Campaign ID": int(data.find("ID").text),
        "Campaign name": data.find("name").text,
        "superCampaignID": "" if data.find("superCampaignID").text is None else int(data.find("superCampaignID").text),
        "superCampaignName": "" if data.find("superCampaignName") is None else data.find("superCampaignName").text,
        "advertiserID": "" if data.find("advertiserID").text is None else int(data.find("advertiserID").text),
        "advertiserAccount": "" if data.find("advertiserAccount") is None else data.find("advertiserAccount").text,
        "assistantAccount": "" if data.find("assistantAccount") is None else data.find("assistantAccount").text,
        "dateStart": "" if data.find("dateStart") is None else data.find("dateStart").text,
        "dateEnd": "" if data.find("dateEnd") is None else data.find("dateEnd").text,
        "dateFinished": "" if data.find("dateFinished") is None else data.find("dateFinished").text,
        "dateAdded": "" if data.find("dateAdded") is None else data.find("dateAdded").text,
        "maxImpressions": "" if data.find("maxImpressions").text is None else int(data.find("maxImpressions").text),
        "impressionsAll": "" if data.find("impressionsAll").text is None else int(data.find("impressionsAll").text)
    }

    campaigns_info_rows.append(campaign_data)

campaigns_info = pd.DataFrame(campaigns_info_rows)

file_name = r'F:\WORK\AdFox\API_Reports\10.01.2024\campaigns_info_short_{}.xlsx'.\
    format(datetime.now().strftime("%Y-%m-%d-%H%M%S"))
campaigns_info.to_excel(file_name)
print('Отчет готов и находится здесь: {}'.format(file_name))
