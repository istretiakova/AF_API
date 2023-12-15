import requests
import pandas as pd
import xml.etree.ElementTree as ET
import time
from settings import TOKEN

file_name = r'F:\WORK\_PBI\Videonet_Monitoring_data\Campaigns_list\campaigns_list_25-27nov2023.xlsx'

def get_dates():
    date_from = "2023-11-25"
    date_to = "2023-11-27"
    return date_from, date_to


def get_campaign_ids_list(date_from, date_to):
    report_id = '4795'
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

    while report_response.json()['result']['state'] != 'SUCCESS':
        print(f"report state = {report_response.json()['result']['state']}")
        time.sleep(10)
        report_response = requests.get(report_url, headers=headers)

    campaign_ids_list = list(pd.DataFrame(data=report_response.json()['result']['table'],
                                          columns=report_response.json()['result']['fields'])['campaignId'])

    return campaign_ids_list


def get_campaign_info(campaign_id):
    headers = {'Authorization': 'OAuth ' + TOKEN}
    url = 'https://adfox.yandex.ru/api/v1'
    campaign_data = {}
    fields = {'ID': 'Campaign ID',
              'name': 'Campaign Name',
              'superCampaignID': 'Supercampaign ID',
              'status': 'status',
              'level': 'level',
              'priority': 'priority',
              'impressionsMethodID': 'impressionsMethodID',
              'impressionsSmoothTypeID': 'impressionsSmoothTypeID',
              'maxImpressions': 'maxImpressions',
              'maxImpressionsPerDay': 'maxImpressionsPerDay',
              'dateStart': 'Campaign dateStart',
              'dateEnd': 'Campaign dateEnd',
              'dateFinished': 'Campaign dateFinished',
              'dateAdded': 'Campaign dateAdded'}

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
    data = root.find("result").find("data")

    for row in data:
        for child in list(row):
            if child.tag in fields.keys():
                field_name = fields[child.tag]
                value = child.text
                campaign_data[field_name] = value

    return campaign_data


def create_campaigns_info(campaign_ids_list):
    campaigns_info_data = []
    campaigns_num = len(campaign_ids_list)
    for num, campaign_id in enumerate(campaign_ids_list):
        print(f'{campaign_id} - {num + 1} кампания из {campaigns_num}')
        campaign_data = get_campaign_info(campaign_id)
        campaigns_info_data.append(campaign_data)

    campaigns_info = pd.DataFrame(campaigns_info_data)
    return campaigns_info


date_from, date_to = get_dates()
campaign_ids_list = get_campaign_ids_list(date_from, date_to)
campaigns_info = create_campaigns_info(campaign_ids_list)

# print(campaigns_info)
campaigns_info.to_excel(file_name)
