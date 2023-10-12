import requests
import pandas as pd
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta

from settings import TOKEN

# file_name = r'F:\WORK\_PBI\Banners_list\banners_list_{}.xlsx'.\
#     format(datetime.now().strftime("%Y-%m-%d-%H%M%S"))

file_name = r'F:\WORK\AdFox\API_Reports\15.09.2023\bn_banners_list{}.xlsx'.\
    format(datetime.now().strftime("%Y-%m-%d-%H%M%S"))


def get_dates():
    date_from = "2023-08-01"
    date_to = "2023-09-14"
    return date_from, date_to


def get_campaigns_list_chunks(date_from, date_to):
    report_id = '5447'
    headers = {'Authorization': 'OAuth ' + TOKEN,
               'Content-Type': 'application/json'}

    task_url = 'https://adfox.yandex.ru/api/report/owner'
    task_params = (
        ('name', 'custom_' + report_id),
        ('dateFrom', date_from),
        ('dateTo', date_to)
    )

    task_response = requests.get(task_url, params=task_params, headers=headers)
    task_id = task_response.json()['result']['taskId']

    report_url = "https://adfox.yandex.ru/api/report/result?taskId=" + task_id
    report_response = requests.get(report_url, headers=headers)

    campaigns_list = list(pd.DataFrame(data=report_response.json()['result']['table'],
                                       columns=report_response.json()['result']['fields'])['campaignId'])

    campaigns_list_chunks = [campaigns_list[x:x+300] for x in range(0, len(campaigns_list), 300)]

    return campaigns_list_chunks


def banners_info(campaigns_list_chunks):
    banners_info_rows = []
    fields = {'ID': 'Banner ID',
              'name': 'Banner Name',
              'campaignID': 'Campaign ID',
              'templateName': 'Template Name',
              'dateStart': 'Banner dateStart',
              'dateEnd': 'Banner dateEnd',
              'dateAdded': 'Banner dateAdded',
              'parameter1': 'Click URL',
              'parameter2': 'parameter2',
              'parameter3': 'parameter3',
              'parameter4': 'parameter4',
              'parameter5': 'parameter5'}

    for chunk in campaigns_list_chunks:

        campaign_ids_list = ','.join(str(x) for x in chunk)
        headers = {'Authorization': 'OAuth ' + TOKEN}
        url = 'https://adfox.yandex.ru/api/v1'
        limit = 1000
        offset = 0
        total_rows = limit + 1
        page = 0
        rows = 0
        while rows + (page - 1) * limit < total_rows:
            print('Данные страницы {} запрошены и обрабатываются'.format(page + 1))
            params = (
                ('object', 'account'),
                ('action', 'list'),
                ('actionObject', 'banner'),
                ('listCampaignIDs', campaign_ids_list),
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
                banner_data = {}
                for child in list(row):
                    if child.tag in fields.keys():
                        field_name = fields[child.tag]
                        value = child.text
                        banner_data[field_name] = value
                banners_info_rows.append(banner_data)
            offset += limit
    banners_info = pd.DataFrame(banners_info_rows)

    return banners_info


date_from, date_to = get_dates()
campaigns_list_chunks = get_campaigns_list_chunks(date_from, date_to)
banners_info = banners_info(campaigns_list_chunks)

# print(banners_info)
banners_info.to_excel(file_name)
