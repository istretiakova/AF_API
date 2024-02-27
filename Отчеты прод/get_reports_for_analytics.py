import requests
import time
import smtplib
import sys
import os
import pandas as pd
import xml.etree.ElementTree as ET

from datetime import datetime, timedelta
from os.path import basename
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate

# ================ Report config =====================

TOKEN = "y0_AgAAAAByRwBUAAr_jgAAAAD04Qm5-BwSIPkOQb6FoeIhgRwzK_Pe59A"
REPORT_IDS = [('03', '6518'),
              ('04', '6519'),
              ('05', '6520'),
              ('12', '6521'),
              ('13', '6522'),
              ('14', '6523'),
              ('15', '6524'),
              ('16', '6525'),
              ('17', '6526'),
              ('18', '6527')]
REPORT_PATH = r'F:\WORK\AdFox\API_Reports\Analytics'

EMAIL_SMTP_SERVER = 'mail.axkv.ru'
EMAIL_PASSWD = 'vI5ykKwkgo'
EMAIL_FROM = 'noreply@axkv.ru'

EMAIL_TO = ['itretiakova@alliance.digital']

EMAIL_MESSAGE = 'Пожалуйста НЕ ОТВЕЧАЙТЕ на это письмо, оно прислано роботом.\n' \
                'Отчет находится в приложении, его можно открыть в Microsoft Excel.'

EMAIL_SUBJECT = 'TEST!!! DA : DCR : Ежедневный отчет по креативам NEW'

# ================ Report config end =====================

headers = {'Authorization': 'OAuth ' + TOKEN,
           'Content-Type': 'application/json'}


def set_report_dates(report_date=None):
    """
        Можно указать кастомную дату для отчета в формате YYYY-MM-DD
        Пример:
        set_report_dates(report_date='2023-12-01')
    """
    print('\r\nЗадаем период отчета set_report_dates()')
    report_date = datetime.now() if report_date is None else datetime.strptime(report_date, '%Y-%m-%d')
    date_to = (report_date - timedelta(days=1)).strftime("%Y-%m-%d")

    if report_date.day == 1:
        date_from = (report_date - timedelta(days=1)).replace(day=1).strftime("%Y-%m-%d")
        date_from_15 = (report_date - timedelta(days=1)).replace(day=16).strftime("%Y-%m-%d")
    elif report_date.day > 1 and report_date.day <= 16:
        date_from = report_date.replace(day=1).strftime("%Y-%m-%d")
        date_from_15 = date_from
    else:
        date_from = report_date.replace(day=1).strftime("%Y-%m-%d")
        date_from_15 = report_date.replace(day=16).strftime("%Y-%m-%d")

    print(f'report_date={report_date}')
    print(f'date_from={date_from}')
    print(f'date_to={date_to}')
    return report_date, date_from, date_from_15, date_to


# def create_report_header(report_name, date_from, date_to):
#     print('\r\nФормируем шапку и путь к файлу для отчета create_report_metadata()')
#     build_on = f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'
#     report_header = [
#         ['Report name', report_name],
#         ['Build on', build_on],
#         ['Date from', date_from],
#         ['Date to', date_to]
#     ]
#     return report_header
#

def create_file_name(report_name):
    out_file_name = r'{}\{}.xlsx'. \
        format(REPORT_PATH, report_name)
    return out_file_name


def remove_previous_report(out_file_name):
    try:
        os.remove(out_file_name)
    except OSError:
        pass


def set_report_task(report_name, report_id, date_from, date_to):
    print(f'\r\nПолучаем данные отчета {report_name}')

    task_url = 'https://adfox.yandex.ru/api/report/owner'
    task_params = (
        ('name', 'custom_' + report_id),
        ('dateFrom', date_from),
        ('dateTo', date_to)
    )
    task_response = requests.get(task_url, params=task_params, headers=headers)
    try:
        task_id = task_response.json()['result']['taskId']
        print(f'task_id = {task_id}')
        return task_id
    except:
        print(task_response.request.headers)
        print(task_response.request.url)
        print(task_response.json())
        sys.exit()


def get_report_data(task_id):
    report_url = "https://adfox.yandex.ru/api/report/result?taskId=" + task_id
    report_response = requests.get(report_url, headers=headers)

    while report_response.json()['result']['state'] != 'SUCCESS':
        print(f"report state = {report_response.json()['result']['state']}")
        time.sleep(10)
        report_response = requests.get(report_url, headers=headers)
    print(f"report state = {report_response.json()['result']['state']}")
    report_data = pd.DataFrame(data=report_response.json()['result']['table'],
                               columns=report_response.json()['result']['fields'])
    return report_data


def export_report_to_file(report_name, report_data, out_file_name):
    remove_previous_report(out_file_name)

    print(f'\r\nЗаписываем отчет {report_name} в файл {out_file_name}')
    writer = pd.ExcelWriter(out_file_name, engine='xlsxwriter',
                            engine_kwargs={'options': {'strings_to_numbers': True,
                                                       'strings_to_urls': False}})
    with writer:
        report_data.to_excel(writer, sheet_name='report', index=False)


def run(report_date=None):
    """
        Можно указать кастомную дату для отчета в формате YYYY-MM-DD
        Пример:
        run(report_date='2023-12-01')
    """
    report_date, date_from, date_from_15, date_to = set_report_dates(report_date=report_date)
    for report_name, report_id in REPORT_IDS:
        out_file_name = create_file_name(report_name)

        if report_name == '15':
            task_id = set_report_task(report_name, report_id, date_from_15, date_to)
        else:
            task_id = set_report_task(report_name, report_id, date_from, date_to)

        report_data = get_report_data(task_id)
        export_report_to_file(report_name, report_data, out_file_name)


if __name__ == '__main__':
    run(report_date='2024-01-01')
