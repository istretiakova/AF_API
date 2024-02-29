import requests
import time
import smtplib
import sys
import os
import shutil
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
REPORT_PATH = r'F:\WORK\AdFox\API_Reports\Analytics\29.02.2024'

EMAIL_SMTP_SERVER = 'mail.axkv.ru'
EMAIL_PASSWD = 'vI5ykKwkgo'
EMAIL_FROM = 'noreply@axkv.ru'

EMAIL_TO = ['itretiakova@alliance.digital']

EMAIL_MESSAGE = 'Пожалуйста НЕ ОТВЕЧАЙТЕ на это письмо, оно прислано роботом.\n' \
                'Отчет находится в приложении, его можно открыть в Microsoft Excel.'

EMAIL_SUBJECT = 'TEST!!! DA : Analytic reports : Ежедневные отчет для аналитики'

# ================ Report config end =====================

headers = {'Authorization': 'OAuth ' + TOKEN,
           'Content-Type': 'application/json'}

columns_names = {
    'correct': 'Полнота данных',
    'date': 'День',
    'siteId': 'ID сайта',
    'siteName': 'Название сайта',
    'advertiserName': 'Рекламодатель',
    'loadsHbIgnored': 'Запросы кода Yandex HB',
    'loadsTotal': 'Запросы кода',
    'loadsCommercial': 'Загрузки баннеров',
    'impressionsCommercial': 'Показы',
    'clicksCommercial': 'Переходы',
    'ctrCommercial': 'CTR',
    'mrc2001Count': 'Показы (IMS)',
    'mrc2002Count': 'Видимые показы (IMS)',
    'mrcViewableRate': 'Доля видимых показов (IMS)',
    'uniqueLoadsTotal': 'Уникальные запросы кода',
    'uniqueImpressionsTotalCorrected': 'Уникальные показы всего',
    'mrc2003Count': 'Показы с неопределенной видимостью (IMS)',
    'uniqueLoadsHbIgnoredCorrected': 'Уникальные запросы кода Yandex HB',
    'uniqueImpressionsCommercialCorrected': 'Уникальные показы',
    'event7Count': 'Событие 7',
    'uniqueLoadsCommercialCorrected': 'Уникальные загрузки баннеров'
}


def set_report_date_to(report_date=None):
    """
        Можно указать кастомную дату для отчета в формате YYYY-MM-DD
        Пример:
        set_report_dates(report_date='2023-12-01')
    """
    print('\r\nЗадаем период отчета set_report_dates()')
    report_date = datetime.now() if report_date is None else datetime.strptime(report_date, '%Y-%m-%d')
    date_to = (report_date - timedelta(days=1)).strftime("%Y-%m-%d")
    print(f'report_date={report_date}')
    print(f'date_to={date_to}')
    return report_date, date_to


def set_report_date_from(report_date):
    if report_date.day == 1:
        date_from = (report_date - timedelta(days=1)).replace(day=1).strftime("%Y-%m-%d")
    else:
        date_from = report_date.replace(day=1).strftime("%Y-%m-%d")
    print(f'date_from={date_from}')
    return date_from


def set_15_report_date_from(report_date):
    if report_date.day == 1:
        date_from = (report_date - timedelta(days=1)).replace(day=21).strftime("%Y-%m-%d")
    elif 1 < report_date.day <= 11:
        date_from = report_date.replace(day=1).strftime("%Y-%m-%d")
    elif 11 < report_date.day <= 21:
        date_from = report_date.replace(day=11).strftime("%Y-%m-%d")
    else:
        date_from = report_date.replace(day=21).strftime("%Y-%m-%d")
    print(f'date_from={date_from}')
    return date_from


def create_file_name(report_name):
    out_file_name = r'{}\{}.xlsx'. \
        format(REPORT_PATH, report_name)
    return out_file_name


def create_file_15_name(report_name, report_date):
    if 1 < report_date.day <= 11:
        suffix = '1'
    elif 11 < report_date.day <= 21:
        suffix = '2'
    else:
        suffix = '3'

    out_file_name = r'{}\{}_{}.xlsx'. \
        format(REPORT_PATH, report_name, suffix)
    return out_file_name


def remove_old_reports(folder):
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))


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


def report_columns_rename(columns):
    for column_num, column_id in enumerate(columns):
        columns[column_num] = columns_names[column_id]
    return columns


def get_report_data(task_id):
    report_url = "https://adfox.yandex.ru/api/report/result?taskId=" + task_id
    report_response = requests.get(report_url, headers=headers)

    while report_response.json()['result']['state'] != 'SUCCESS':
        print(f"report state = {report_response.json()['result']['state']}")
        time.sleep(10)
        report_response = requests.get(report_url, headers=headers)
    print(f"report state = {report_response.json()['result']['state']}")
    report_table = report_response.json()['result']['table']

    report_columns = report_columns_rename(report_response.json()['result']['fields'])

    report_totals = ['Всего'] + list(report_response.json()['result']['totals'].values())
    report_table.append(report_totals)
    report_data = pd.DataFrame(data=report_table, columns=report_columns)

    if 'День' in report_data.columns:
        report_data = report_data.astype({'День': 'datetime64[ns]'})

    return report_data


def export_report_to_file(report_name, report_data, out_file_name):

    print(f'\r\nЗаписываем отчет {report_name} в файл {out_file_name}')
    writer = pd.ExcelWriter(out_file_name, engine='xlsxwriter',
                            engine_kwargs={'options': {'strings_to_numbers': True,
                                                       'strings_to_urls': False}},
                            datetime_format='dd.mm.yyyy')
    with writer:
        report_data.to_excel(writer, sheet_name='report', index=False)


def send_reports(folder):
    print('Отправляем отчет по списку рассылки')
    msg = MIMEMultipart()
    msg['From'] = EMAIL_FROM
    msg['To'] = ','.join(EMAIL_TO)
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = EMAIL_SUBJECT

    msg.attach(MIMEText(EMAIL_MESSAGE))
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        with open(file_path, "rb") as file:
            part = MIMEApplication(
                file.read(),
                Name=basename(file_path)
            )
        part['Content-Disposition'] = 'attachment; filename="%s"' % basename(file_path)
        msg.attach(part)

    server = smtplib.SMTP(EMAIL_SMTP_SERVER)
    server.set_debuglevel(True)
    server.starttls()
    server.login(EMAIL_FROM, EMAIL_PASSWD)
    server.sendmail(EMAIL_FROM, EMAIL_TO, msg.as_string())
    server.quit()
    print('Отчет отправлен по списку рассылки')


def run(report_date=None):
    """
        Можно указать кастомную дату для отчета в формате YYYY-MM-DD
        Пример:
        run(report_date='2023-12-01')
    """
    remove_old_reports(REPORT_PATH)
    report_date, date_to = set_report_date_to(report_date=report_date)
    for report_name, report_id in REPORT_IDS:

        if report_name == '15':
            out_file_name = create_file_15_name(report_name, report_date)
            date_from = set_15_report_date_from(report_date=report_date)
        else:
            out_file_name = create_file_name(report_name)
            date_from = set_report_date_from(report_date=report_date)

        task_id = set_report_task(report_name, report_id, date_from, date_to)
        report_data = get_report_data(task_id)
        export_report_to_file(report_name, report_data, out_file_name)
    send_reports(REPORT_PATH)


if __name__ == '__main__':
    run(report_date='2024-02-29')
