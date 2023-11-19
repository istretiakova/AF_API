import requests
import pandas as pd
import xml.etree.ElementTree as ET

from settings import TOKEN

file_name = r'F:\WORK\_PBI\Videonet_Monitoring_data\Supercampaigns_list\supercampaigns_list_11-12nov2023.xlsx'

def get_dates():
    date_from = "2023-11-11"
    date_to = "2023-11-12"
    return date_from, date_to


def get_supercampaign_ids_list(date_from, date_to):
    report_id = '4798'
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

    supercampaign_ids_list = list(pd.DataFrame(data=report_response.json()['result']['table'],
                                               columns=report_response.json()['result']['fields'])['supercampaignId'])

    return supercampaign_ids_list


def get_supercampaign_info(supercampaign_id):
    headers = {'Authorization': 'OAuth ' + TOKEN}
    url = 'https://adfox.yandex.ru/api/v1'
    supercampaign_data = {}
    fields = {'ID': 'Supercampaign ID',
              'name': 'Supercampaign Name',
              'advertiserID': 'Advertiser ID',
              'assistantID': 'Assistant ID',
              'logicType': 'logicType',
              'type': 'type',
              'level': 'level',
              'priority': 'priority',
              'status': 'status',
              'impressionsMethodID': 'impressionsMethodID',
              'maxImpressions': 'maxImpressions',
              'maxImpressionsPerDay': 'maxImpressionsPerDay',
              'maxUniqueImpressions': 'maxUniqueImpressions',
              'datePeriod': 'datePeriod',
              'frequencyTypeImpressions': 'frequencyTypeImpressions',
              'uniquePeriodImpressions': 'uniquePeriodImpressions',
              'impressionsPerPeriod': 'impressionsPerPeriod',
              'minimalPeriodImpressions': 'minimalPeriodImpressions',
              'dateStart': 'dateStart',
              'dateEnd': 'dateEnd',
              'dateFinished': 'dateFinished','dateAdded': 'dateAdded'}

    params = (
        ('object', 'account'),
        ('action', 'list'),
        ('actionObject', 'superCampaign'),
        ('actionObjectID', supercampaign_id),
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
                supercampaign_data[field_name] = value

    return supercampaign_data


def create_supercampaigns_info(supercampaign_ids_list):
    supercampaigns_info_data = []
    supercampaigns_num = len(supercampaign_ids_list)
    for num, supercampaign_id in enumerate(supercampaign_ids_list):
        print(f'{supercampaign_id} - {num + 1} суперкампания из {supercampaigns_num}')
        supercampaign_data = get_supercampaign_info(supercampaign_id)
        supercampaigns_info_data.append(supercampaign_data)

    supercampaigns_info = pd.DataFrame(supercampaigns_info_data)
    return supercampaigns_info


date_from, date_to = get_dates()
supercampaign_ids_list = get_supercampaign_ids_list(date_from, date_to)
supercampaigns_info = create_supercampaigns_info(supercampaign_ids_list)

# print(supercampaigns_info)
supercampaigns_info.to_excel(file_name)
