# -*- coding: utf-8 -*-
"""
Created on Fri Oct 28 17:44:36 2021

@author: Irina Tretiakova

Изменяем значение поля user1 для списка баннеров

"""

import pandas as pd
import xml.etree.ElementTree as ET
import requests
from datetime import datetime
from settings import ADFOX_API_KEY

headers = {'X-Yandex-API-Key': ADFOX_API_KEY}
url = 'https://adfox.yandex.ru/api/v1'

# ==========Конфиг==========

files_url = r'F:\WORK\AdFox\API_Reports\15.03.2023\\'
in_file = f'{files_url}u_inapp_banners.csv'
out_file = f'{files_url}banners_changes_{datetime.now().strftime("%Y-%m-%d-%H%M%S")}.xlsx'

# =======Конец конфига=======

banners_list = pd.read_csv(in_file, encoding='utf8')['ID баннера'].tolist()
banners_num = len(banners_list)
banner_changes_data = pd.DataFrame(columns=["bannerID", "old_value", "new_value", "error_code"])

for n, banner_id in enumerate(banners_list):

    get_params = (
        ('object', 'account'),
        ('action', 'list'),
        ('actionObject', 'banner'),
        ('actionObjectID', banner_id)
    )

    get_response = requests.get(url, params=get_params, headers=headers)
    get_root = ET.fromstring(get_response.text)

    parameter1_value = get_root.find("result").find("data").find("row0").find("parameter1").text
    parameter1_new_value = parameter1_value.replace("sa.rtb.mts.ru", "inpp.mts.ru").replace("&page", "&bundle")

    # parameter1_new_value = parameter1_value + "&puid1=%request.puid1%&puid4=%request.puid4%&puid5=%request.puid5%" \
    #                                           "&puid6=%request.puid6%&puid7=%request.puid7%&puid8=%request.puid8%" \
    #                                           "&puid9=%request.puid9%&puid17=%request.puid17%&puid21=%request.puid21%" \
    #                                           "&puid22=%request.puid22%&puid23=%request.puid23%" \
    #                                           "&puid27=%request.puid27%&puid62=%request.puid62%&puid63=%request.puid63%"

    # trackingURL_value = get_root.find("result").find("data").find("row0").find("trackingURL").text
    # trackingURL_new_value = trackingURL_value.replace('https://www.tns-counter.ru/V13a**%request.eid3%**idsh_vmon/ru/'
    #                                                   'CP1251/tmsec=idsh_dtotal/%request.timestamp%|', '')

    set_params = (
        ('object', 'banner'),
        ('action', 'modify'),
        ('actionObject', 'banner'),
        ('objectID', banner_id),
        ('user1', parameter1_new_value),
        ('encoding', 'UTF-8')
    )

    set_response = requests.get(url, params=set_params, headers=headers)
    set_root = ET.fromstring(set_response.text)
    set_error_code = set_root.find("status").find("code").text

    # set_error_code = ''
    print(f'Обрабатывается баннер {n+1} из {banners_num} id {banner_id}, error code - {set_error_code}')

    banner_changes = pd.Series({"bannerID": banner_id,
                                "old_value": parameter1_value,
                                "new_value": parameter1_new_value,
                                "error_code": set_error_code}
                               )

    banner_changes_data = pd.concat([banner_changes_data, banner_changes.to_frame().T], ignore_index=True)

banner_changes_data.to_excel(out_file)
print("Изменения в баннеры внесены, отчет об изменениях находится здесь", out_file)
