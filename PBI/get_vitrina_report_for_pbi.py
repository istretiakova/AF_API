import requests
import pandas as pd
from datetime import datetime, timedelta

from settings import TOKEN


def get_dates():
    date_from = datetime.strftime(datetime(datetime.now().year, datetime.now().month-3, 1), '%Y-%m-%d')
    date_to = datetime.strftime(datetime.now() - timedelta(1), '%Y-%m-%d')
    return date_from, date_to


def get_vitrina_report(date_from, date_to):
    report_id = '4843'
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
    state = ''

    while state != 'SUCCESS':
        state = report_response.json()['result']['state']

    report = pd.DataFrame(data=report_response.json()['result']['table'],
                                  columns=report_response.json()['result']['fields'])
    return report


date_from, date_to = get_dates()
vitrina_report = get_vitrina_report(date_from, date_to)
print(vitrina_report)
