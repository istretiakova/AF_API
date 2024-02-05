import requests
import time
import smtplib
import pandas as pd

from datetime import datetime, timedelta
from os import path, makedirs
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate

from settings import TOKEN

pd.options.mode.chained_assignment = None  # default='warn'

# ================ Report config =====================

TRACKERS_DATA_REPORT_ID = "6242"
TRACKERS_BASE_PATH = r'F:\WORK\Mediascope\AdCampaigns'

EMAIL_SMTP_SERVER = 'mail.axkv.ru'
EMAIL_PASSWD = 'vI5ykKwkgo'
EMAIL_FROM = 'noreply@axkv.ru'

EMAIL_TO = ['itretiakova@alliance.digital',
            'adcampaigns@mediascope.net',
            'adcounter@mediascope.net']

EMAIL_MESSAGE = 'Счетчики для кампании superCampaignID '

EMAIL_SUBJECT = 'superCampaignID '

# ================ Report config end =====================


class SentTrackersToAdcampaigns():

    def __init__(self, report_date=None):
        self.report_date = datetime.now() if report_date is None else datetime.strptime(report_date, '%Y-%m-%d')
        self.date_from = ''
        self.date_to = ''
        self.trackers_folder = ''
        self.trackers_data = pd.DataFrame()
        self.supercampaigns_list = []

    def set_dates(self):
        print('\r\nЗадаем период отчета set_dates()')
        last_report_month_day = self.report_date.replace(day=1) - timedelta(days=1)
        self.date_from = last_report_month_day.replace(day=1).strftime("%Y-%m-%d")
        self.date_to = last_report_month_day.strftime("%Y-%m-%d")
        print(f'report_date={self.report_date}')
        print(f'date_from={self.date_from}')
        print(f'date_to={self.date_to}')

    def create_trackers_folder(self):
        print(f'Создаем папку для хранения файлов со счетчиками create_trackers_folder(self)')
        self.trackers_folder = path.join(TRACKERS_BASE_PATH, datetime.now().strftime("%Y-%m-%d-%H%M%S"))
        if not path.exists(self.trackers_folder):
            makedirs(self.trackers_folder)
        print(f'Папка со счетчиками {self.trackers_folder}')

    def get_trackers_data(self):
        print('Получаем базовый отчет с данными для трекеров get_trackers_data(self)')
        report_id = TRACKERS_DATA_REPORT_ID
        headers = {'Authorization': 'OAuth ' + TOKEN,
                   'Content-Type': 'application/json'}

        task_url = 'https://adfox.yandex.ru/api/report/owner'
        task_params = (
            ('name', 'custom_' + report_id),
            ('dateFrom', self.date_from),
            ('dateTo', self.date_to)
        )

        task_response = requests.get(task_url, params=task_params, headers=headers)
        task_id = task_response.json()['result']['taskId']

        report_url = "https://adfox.yandex.ru/api/report/result?taskId=" + task_id
        report_response = requests.get(report_url, headers=headers)

        while report_response.json()['result']['state'] != 'SUCCESS':
            print(f"report state = {report_response.json()['result']['state']}")
            time.sleep(10)
            report_response = requests.get(report_url, headers=headers)
        print(f"report state = {report_response.json()['result']['state']}")
        self.trackers_data = pd.DataFrame(data=report_response.json()['result']['table'],
                                         columns=report_response.json()['result']['fields'])
        print(self.trackers_data.info())

    def get_supercampaigns_list(self):
        print('Получаем список суперкампаний get_supercampaigns_list(self)')
        self.supercampaigns_list = self.trackers_data.supercampaignId.drop_duplicates().to_list()
        print(len(self.supercampaigns_list))

    def create_supercampaign_trackers_list(self, supercampaign_id):
        print(f'формируем трекеры для суперкампании create_supercampaign_trackers_list(self, {supercampaign_id})')
        supercampaign_data = self.trackers_data[self.trackers_data['supercampaignId'] == supercampaign_id]
        print(supercampaign_data)
        supercampaign_data['counter1'] = supercampaign_data.apply(lambda x: f'idsh_sc{x.supercampaignId}-fl{x.campaignId}', axis=1)
        supercampaign_data['counter2'] = supercampaign_data['counter1']
        supercampaign_trackers_list = supercampaign_data[['counter1', 'counter2']]
        return supercampaign_trackers_list

    def create_trackers_file_path(self, supercampaign_id):
        trackers_file_name = f'superCampaignID {supercampaign_id}.csv'
        trackers_file_path = path.join(self.trackers_folder, trackers_file_name)
        return trackers_file_path

    @staticmethod
    def create_message_text(supercampaign_id):
        message_text = f'{EMAIL_MESSAGE} {supercampaign_id}'
        return message_text

    @staticmethod
    def create_message_subject(supercampaign_id):
        message_subject = f'{EMAIL_SUBJECT} {supercampaign_id}'
        return message_subject

    def create_trackers_file(self, supercampaign_id):
        trackers_list = self.create_supercampaign_trackers_list(supercampaign_id)
        file_name = self.create_trackers_file_path(supercampaign_id)
        trackers_list.to_csv(file_name, sep=';', encoding='utf-8', header=False, index=False)
        return file_name

    def sent_file_to_adcampaigns(self, trackers_file, supercampaign_id):
        print('Отправляем отчет по списку рассылки')
        msg = MIMEMultipart()
        msg['From'] = EMAIL_FROM
        msg['To'] = ','.join(EMAIL_TO)
        msg['Date'] = formatdate(localtime=True)
        msg['Subject'] = self.create_message_subject(supercampaign_id)

        msg.attach(MIMEText(self.create_message_text(supercampaign_id)))

        with open(trackers_file, "rb") as file:
            part = MIMEApplication(
                file.read(),
                Name=path.basename(trackers_file)
            )
        part['Content-Disposition'] = 'attachment; filename="%s"' % path.basename(trackers_file)
        msg.attach(part)

        server = smtplib.SMTP(EMAIL_SMTP_SERVER)
        server.set_debuglevel(True)
        server.starttls()
        server.login(EMAIL_FROM, EMAIL_PASSWD)
        server.sendmail(EMAIL_FROM, EMAIL_TO, msg.as_string())
        server.quit()
        print('Отчет отправлен по списку рассылки')

    def create_and_send_trackers(self):
        print(f'формируем счетчики для суперкампаний и сохраняем их в отдельные файлы')
        for supercampaign_id in self.supercampaigns_list:
            print(f'формируем и сохраняем счетчики для суперкампании {supercampaign_id}')
            trackers_file = self.create_trackers_file(supercampaign_id)
            self.sent_file_to_adcampaigns(trackers_file, supercampaign_id)

    def run(self):
        self.set_dates()
        self.create_trackers_folder()
        self.get_trackers_data()
        self.get_supercampaigns_list()
        self.create_and_send_trackers()


if __name__ == '__main__':
    # process = SentTrackersToAdcampaigns(report_date='2023-12-01')
    process = SentTrackersToAdcampaigns()
    process.run()



