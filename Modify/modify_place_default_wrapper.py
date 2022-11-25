# -*- coding: utf-8 -*-
"""
Created on Fri Oct 28 17:44:36 2021

@author: Irina Tretiakova

Изменяем код дефолтного баннера для списка площадок на универсальный wrapper с уникальным пассбэк-тегом паблишера

"""

import pandas as pd
import xml.etree.ElementTree as ET
import requests
from datetime import datetime
from settings import ADFOX_API_KEY
import xmltodict

headers = {'X-Yandex-API-Key': ADFOX_API_KEY}
url = 'https://adfox.yandex.ru/api/v1'

# ==========Конфиг==========

files_url = r'F:\WORK\AdFox\API_Reports\01.11.2022\\'
in_file = f'{files_url}tvzvezda_places.csv'
out_file = f'{files_url}tvzvezda_places_default_banners_changes_{datetime.now().strftime("%Y-%m-%d-%H%M%S")}.xlsx'

# =======Конец конфига=======

places_list = pd.read_csv(in_file, encoding='utf8')['ID площадки'].tolist()
places_num = len(places_list)
places_changes_data = pd.DataFrame(columns=["placeID", "old_default_code", "new_default_code", "error_code"])

offset = 0
limit = 1000

for n, place_id in enumerate(places_list):

    get_params = (
        ('object', 'account'),
        ('action', 'list'),
        ('actionObject', 'defaultBanner'),
        ('listPlaceIDs', place_id),
        ('offset', offset),
        ('limit', limit),
        ('encoding', 'UTF-8')
    )

    get_response = requests.get(url, params=get_params, headers=headers)
    get_response_dict = xmltodict.parse(get_response.text)

    old_default_code = get_response_dict['response']['result']['data']['row0']['defaultCode']

    vast_data = xmltodict.parse(old_default_code)
    passback_url = vast_data['VAST']['Ad']['Wrapper']['VASTAdTagURI']


    new_default_code ='<?xml version="1.0" encoding="UTF-8"?>\n' \
                      '<VAST version="2.0">\n' \
                      '  <Ad id="defaultwrapper">\n' \
                      '    <Wrapper>\n' \
                      '      <AdSystem>AdFox.ru</AdSystem>\n' \
                      '      <VASTAdTagURI><![CDATA[' + passback_url + ']]></VASTAdTagURI>\n' \
                      '      <Error><![CDATA[https://www.tns-counter.ru/V13a**%request.eid3%**idsh_vmon/ru/CP1251/tmsec=idsh_vtotal/%request.timestamp%]]></Error>\n' \
                      '      <Error><![CDATA[https://www.tns-counter.ru/V13a**%request.eid3%**idsh_vid/ru/CP1251/tmsec=idsh_sid%site.id%-vitid1/%request.timestamp%]]></Error>\n' \
                      '      <Error><![CDATA[https://mc.yandex.ru/watch/66716692?page-url=%site.id%%3Futm_source=vn_default_error%26utm_medium=%26utm_campaign=%campaign.id%%26utm_content=%banner.id%%26utm_term=%supercampaign.id%&page-ref=%request.referrer:urlenc%]]></Error>\n' \
                      '      <Error><![CDATA[https://bridgertb.tech/ssp/sync/da_bridge?sspuid=%system.random%]]></Error>\n' \
                      '      <Error><![CDATA[https://px802%system.random%.mediahils.ru/s.gif?userid=%request.eid3%&media=video]]></Error>\n' \
                      '      <Impression></Impression>\n' \
                      '      <Creatives></Creatives>\n' \
                      '      <Extensions>\n' \
                      '        <Extension type="CustomTracking">\n' \
                      '          <Tracking event="onVastLoad"><![CDATA[https://www.tns-counter.ru/V13a**%request.eid3%**idsh_vmon/ru/CP1251/tmsec=idsh_vtotal/%request.timestamp%]]></Tracking>\n' \
                      '          <Tracking event="onVastLoad"><![CDATA[https://www.tns-counter.ru/V13a**%request.eid3%**idsh_vid/ru/CP1251/tmsec=idsh_sid%site.id%-vitid1/%request.timestamp%]]></Tracking>\n' \
                      '          <Tracking event="onVastLoad"><![CDATA[https://mc.yandex.ru/watch/66716692?page-url=%site.id%%3Futm_source=%26utm_medium=%26utm_campaign=%campaign.id%%26utm_content=%banner.id%%26utm_term=%supercampaign.id%&page-ref=%request.referrer:urlenc%]]></Tracking>\n' \
                      '          <Tracking event="onVastLoad"><![CDATA[https://mc.yandex.ru/watch/50061703?page-url=%site.id%%3Futm_source=%26utm_medium=%request.eid1%%26utm_campaign=%campaign.id%%26utm_content=%banner.id%%26utm_term=%supercampaign.id%&page-ref=%request.referrer:urlenc%]]></Tracking>\n' \
                      '          <Tracking event="onVastLoad"><![CDATA[https://bridgertb.tech/ssp/sync/da_bridge?sspuid=%system.random%]]></Tracking>\n' \
                      '          <Tracking event="onVastLoad"><![CDATA[https://px802%system.random%.mediahils.ru/s.gif?userid=%request.eid3%&media=video]]></Tracking>\n' \
                      '        </Extension>\n' \
                      '      </Extensions>\n' \
                      '    </Wrapper>\n' \
                      '  </Ad>\n' \
                      '</VAST>'

    set_params = (
        ('object', 'place'),
        ('action', 'updateDefaultBanner'),
        ('objectID', place_id),
        ('mode', 1),
        ('defaultCode', new_default_code)
    )

    set_response = requests.get(url, params=set_params, headers=headers)
    set_root = ET.fromstring(set_response.text)
    set_error_code = set_root.find("status").find("code").text

    print(f'Обрабатывается площадка {n+1} из {places_num} id {place_id}, error code - {set_error_code}')
#    print(f'Обрабатывается площадка {n + 1} из {places_num} id {place_id}')

    place_changes = pd.Series({"placeID": place_id,
                               "old_default_code": old_default_code,
                               "passback URL": passback_url,
                               "new_default_code": new_default_code,
                               "error_code": set_error_code}
                              )

    places_changes_data = pd.concat([places_changes_data, place_changes.to_frame().T], ignore_index=True)

places_changes_data.to_excel(out_file)
print("Дефолтные баннеры площадок исправлены, отчет об изменениях находится здесь", out_file)
