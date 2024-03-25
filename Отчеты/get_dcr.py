import requests
import pandas as pd
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
import time
from settings import TOKEN, EMAIL_LOGIN, EMAIL_PASSWD, EMAIL_FROM, EMAIL_TO, EMAIL_MESSAGE, EMAIL_SUBJECT, \
    EMAIL_SMTP_SERVER

import smtplib
from os.path import basename
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate

class GetDcrReport:
    """
        Можно указать кастомную дату для отчета в формате YYYY-MM-DD
        Пример:
        GetDcrReport(report_date='2023-12-01')
    """

    def __init__(self, report_date=None, out_file_name=None):
        self.report_date = datetime.now() if report_date is None else datetime.strptime(report_date, '%Y-%m-%d')
        self.date_from = ''
        self.date_to = ''
        self.out_file_name = ''
        self.campaigns_list_chunks = []
        self.banners_chunk = 0
        self.banners_info_rows = []
        self.banners_info = pd.DataFrame()
        self.advertisers_list = pd.DataFrame()
        self.assistants_list = pd.DataFrame()
        self.report_header = []
        self.banners_list = pd.DataFrame()

    def set_dates(self):
        print('\r\nЗадаем период отчета set_dates()')
        if self.report_date.day == 1:
            self.date_from = (self.report_date - timedelta(days=1)).replace(day=1).strftime("%Y-%m-%d")
            self.date_to = (self.report_date - timedelta(days=1)).strftime("%Y-%m-%d")
        else:
            self.date_from = self.report_date.replace(day=1).strftime("%Y-%m-%d")
            self.date_to = self.report_date.strftime("%Y-%m-%d")
        print(f'report_date={self.report_date}')
        print(f'date_from={self.date_from}')
        print(f'date_to={self.date_to}')

    def create_report_metadata(self):
        print('Формируем шапку для отчета create_report_header(self)')
        build_on = f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'
        self.report_header = [
            ['Report name', 'Ежедневный отчет по креативам'],
            ['Build on', build_on],
            ['Date from', self.date_from],
            ['Date to', self.date_to]
        ]
        self.out_file_name = r'F:\WORK\AdFox\API_Reports\DCR\dcr-report_01-{}_{}.xlsx'. \
            format(datetime.strptime(self.date_to, '%Y-%m-%d').strftime('%d.%m.%Y'),
                   datetime.now().strftime("%Y%m%d%H%M%S"))

    def get_banners_list(self):
        print('Получаем список баннеров текущего месяца get_banners_impressions(self)')
        report_id = '5945'
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
        self.banners_list = pd.DataFrame(data=report_response.json()['result']['table'],
                                         columns=report_response.json()['result']['fields'])
        print(self.banners_list.info())

    def get_campaigns_list_chunks(self):
        print('Получаем список кампаний текущего месяца get_campaigns_list_chunks(self)')
        report_id = '4795'
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
        campaigns_list = list(pd.DataFrame(data=report_response.json()['result']['table'],
                                           columns=report_response.json()['result']['fields'])['campaignId'])
        self.campaigns_list_chunks = [campaigns_list[x:x + 300] for x in range(0, len(campaigns_list), 300)]
        print(f'Получили {len(self.campaigns_list_chunks)} списка ID кампаний\r\n')

    @staticmethod
    def get_mediaplan_id(campaign_name):
        if campaign_name.find(':') > -1:
            try:
                mediaplan_id = int(campaign_name.split(':', 1)[0])
            except:
                mediaplan_id = campaign_name.split(':', 1)[0]
        else:
            mediaplan_id = ''
        return mediaplan_id

    @staticmethod
    def get_verifier(media_url):
        if isinstance(media_url, str):
            if media_url.find('wcm') > -1:
                verifier = 'weborama'
            elif media_url.find('adriver') > -1:
                verifier = 'adriver'
            elif media_url.find('5vision') > -1:
                verifier = 'brain'
            elif media_url.find('bs.serving-sys') > -1:
                verifier = 'sizmek'
            elif media_url.find('cdnvideo') > -1:
                verifier = 'none'
            elif media_url.find('selcdn') > -1:
                verifier = 'getshop'
            elif media_url.find('selstorage') > -1:
                verifier = 'getshop'
            elif media_url.find('getshop') > -1:
                verifier = 'getshop'
            else:
                verifier = 'other'
        else:
            verifier = ''
        return verifier

    @staticmethod
    def get_admon_state(template_name):
        if isinstance(template_name, str):
            if template_name.find('Admon') > -1:
                admon_state = 'с Admon'
            else:
                admon_state = 'без Admon'
        else:
            admon_state = ''
        return admon_state

    @staticmethod
    def get_status_name(status):
        states = {0: 'активный',
                  1: 'приостановленный',
                  2: 'завершенный'}
        status_name = states[status]
        return status_name

    @staticmethod
    def get_agency(advertiser_name, company_name):
        adv_name = company_name if company_name is not None else advertiser_name
        try:
            agency = adv_name.split('_', 1)[0]
        except:
            agency = ''
        return agency

    @staticmethod
    def get_advertiser(advertiser_name, company_name):
        adv_name = company_name if company_name is not None else advertiser_name
        try:
            advertiser = adv_name.split('_', 1)[1]
        except:
            advertiser = ''
        return advertiser

    @staticmethod
    def check_erid_error(media_url='', click_url='', erid=''):
        errors_list = []
        if str(erid) == '':
            errors_list.append('Не заполнен ERID')
        if str(click_url).find('%user3%') == -1:
            errors_list.append('Click URL не содержит ERID')
        if str(media_url).find('cdnvideo') == -1 & str(media_url).find('%user3') == -1:
            errors_list.append('Код верификатора не содержит ERID')
        errors_string = ', '.join(errors_list)
        return errors_string

    @staticmethod
    def calc_dropoff(loads, impressions):
        try:
            dropoff = str(round((1 - impressions / loads) * 100)) + '%'
        except:
            dropoff = ''
        return dropoff

    def get_banners_list_chunk(self, campaigns_list):
        print(f'\r\nПолучаем инфо о баннерах из {self.banners_chunk + 1} '
              f'части списка кампаний get_banners_list_chunk(self, campaigns_list)')
        campaign_ids_list = ','.join(str(x) for x in campaigns_list)
        headers = {'Authorization': 'OAuth ' + TOKEN}
        url = 'https://adfox.yandex.ru/api/v1'
        limit = 1000
        offset = 0
        total_rows = limit + 1
        page = 0
        rows = 0
        while rows + (page - 1) * limit < total_rows:
            print(f'Данные для {page + 1} группы баннеров из {self.banners_chunk + 1} '
                  f'списка ID запрошены и обрабатываются')
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
            data = root.find("result").find("data")
            for row in data:
                banner_data = {}
                for child in list(row):
                    try:
                        value = int(child.text)
                    except:
                        value = child.text
                    banner_data[child.tag] = value
                self.banners_info_rows.append(banner_data)
            offset += limit
            page += 1
        self.banners_chunk += 1

    def get_banners_info_list(self):
        print('Запускаем сбор инфо о баннерах из кампаний текущего месяца get_banners_list(self)')
        for chunk in self.campaigns_list_chunks:
            self.get_banners_list_chunk(chunk)
        print('Записываем инфо о баннерах из кампаний текущего месяца в датафрейм')
        self.banners_info = pd.DataFrame(self.banners_info_rows)
        print(self.banners_info.info())

    def get_advertisers_list(self):
        print('\nВыгружаем справочник рекламодателей get_advertisers_list()')
        headers = {'Authorization': 'OAuth ' + TOKEN}
        url = 'https://adfox.yandex.ru/api/v1'
        limit = 1000
        offset = 0
        total_rows = limit + 1
        page = 0
        rows = 0

        fields = {'ID': 'Advertiser ID',
                  'company': 'Advertiser company'}

        advertisers_info_rows = []

        while rows + (page - 1) * limit < total_rows:
            print('Данные страницы {} запрошены и обрабатываются'.format(page + 1))

            params = (
                ('object', 'account'),
                ('action', 'list'),
                ('actionObject', 'advertiser'),
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
                advertiser_data = {}
                for child in list(row):
                    if child.tag in fields:
                        field_name = fields[child.tag]
                        try:
                            value = int(child.text)
                        except:
                            value = child.text
                        advertiser_data[field_name] = value
                advertisers_info_rows.append(advertiser_data)
            offset += limit
        self.advertisers_list = pd.DataFrame(advertisers_info_rows)

    def add_info_to_banners_list(self):
        print('\r\nОбъединяем список баннеров с инфо о баннерах add_info_to_banners_list(self)')
        self.banners_list = self.banners_list.merge(self.banners_info, how='inner',
                                                    left_on='bannerId', right_on='ID')
        self.banners_list['status'] = self.banners_list['status'].apply(lambda x: self.get_status_name(x))
        self.banners_list['Verifier'] = self.banners_list['parameter1'].apply(lambda x: self.get_verifier(x))
        self.banners_list['Admon'] = self.banners_list['templateName'].apply(lambda x: self.get_admon_state(x))
        self.banners_list['Mediaplan ID'] = self.banners_list['campaignName'].apply(lambda x: self.get_mediaplan_id(x))
        self.banners_list = self.banners_list.merge(self.advertisers_list, how='left',
                                                    left_on='advertiserId', right_on='Advertiser ID')
        self.banners_list['Agency'] = self.banners_list.\
            apply(lambda x: self.get_agency(x['advertiserName'], x['Advertiser company']), axis=1)
        self.banners_list['Advertiser'] = self.banners_list. \
            apply(lambda x: self.get_advertiser(x['advertiserName'], x['Advertiser company']), axis=1)
        self.banners_list['ERID errors'] = self.banners_list.\
            apply(lambda x: self.check_erid_error(x['parameter1'], x['parameter2'], x['parameter3']), axis=1)
        self.banners_list['Dropoff %'] = self.banners_list. \
            apply(lambda x: self.calc_dropoff(x['loadsCommercial'], x['impressionsCommercial']), axis=1)

    def set_columns_order(self):
        print('\r\nОставляем только нужные колонки и переименовываем их set_columns_order(self)')
        fields = {'bannerId': 'ID баннера',
                  'name': 'Название баннера',
                  'campaignID': 'ID кампании',
                  'campaignName': 'Название кампании',
                  'campaignAssistantName': 'Ассистент',
                  'advertiserId': 'ID рекламодателя',
                  'advertiserName': 'Рекламодатель AdFox',
                  'Advertiser company': 'Компания рекламодателя AdFox',
                  'Agency': 'Агентство',
                  'Advertiser': 'Рекламодатель',
                  'Mediaplan ID': 'ID медиаплана',
                  'loadsCommercial': 'Загрузки баннеров',
                  'impressionsCommercial': 'Показы',
                  'Dropoff %': 'Dropoff %',
                  'Verifier': 'Верификатор',
                  'Admon': 'Верификация Admon',
                  'parameter3': 'ERID',
                  'ERID errors': 'Ошибки передачи ERID',
                  'parameter4': 'Длительность',
                  'parameter24': 'SkipTime2',
                  'status': 'Статус',
                  'templateName': 'Назание шаблона',
                  'parameter1': 'URL видеоролика',
                  'parameter2': 'Click URL',
                  'parameter7': 'URLMOD final',
                  'parameter9': 'impression1',
                  'parameter10': 'impression2',
                  'parameter11': 'impression3',
                  'parameter12': 'impression4',
                  'dateAdded': 'Дата добавления баннера',
                  'dateStart': 'Дата старта баннера',
                  'dateEnd': 'Дата финиша баннера',
                  'campaignDateStart': 'Дата старта кампании',
                  'campaignDateEnd': 'Дата финиша кампании'}
        self.banners_list = self.banners_list[fields.keys()]
        self.banners_list = self.banners_list.rename(columns=fields)
        print(self.banners_list.info())

    def export_to_file(self):
        print('\r\nЗаписываем данные в файл export_to_file(self)')
        writer = pd.ExcelWriter(self.out_file_name, engine='xlsxwriter',
                                engine_kwargs={'options': {'strings_to_numbers': True,
                                                           'strings_to_urls': False}})
        with writer:
            self.banners_list.to_excel(writer, sheet_name='report', index=False, startrow=7)
            workbook = writer.book
            worksheet = writer.sheets["report"]
            (max_row, max_col) = self.banners_list.shape
            max_row += 7
            column_settings = [{"header": column} for column in self.banners_list.columns]
            worksheet.add_table(7, 0, max_row, max_col - 1,
                                {"columns": column_settings, "style": "Table Style Medium 2"})
            header_h_format = workbook.add_format({'bold': 1,
                                                   'border': 1,
                                                   'font_color': '#FFFFFF',
                                                   'bg_color': '#4F81BD',
                                                   'border_color': '#95B3D7'})
            row_1_format = workbook.add_format({'border': 1,
                                                'font_color': '#000000',
                                                'bg_color': '#DCE6F1',
                                                'border_color': '#95B3D7'})
            row_2_format = workbook.add_format({'border': 1,
                                                'font_color': '#000000',
                                                'border_color': '#95B3D7'})

            worksheet.write(0, 0, self.report_header[0][0], header_h_format)
            worksheet.write(0, 1, self.report_header[0][1], header_h_format)
            worksheet.write(1, 0, self.report_header[1][0], row_1_format)
            worksheet.write(1, 1, self.report_header[1][1], row_1_format)
            worksheet.write(2, 0, self.report_header[2][0], row_2_format)
            worksheet.write(2, 1, self.report_header[2][1], row_2_format)
            worksheet.write(3, 0, self.report_header[3][0], row_1_format)
            worksheet.write(3, 1, self.report_header[3][1], row_1_format)

            thin_cols_list = [0, 2, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16,
                              18, 19, 20, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33]
            wide_cols_list = [1, 3, 17, 21, 22, 23]

            for col in thin_cols_list:
                worksheet.set_column(col, col, 12)

            for col in wide_cols_list:
                worksheet.set_column(col, col, 40)

        print(f'Отчет готов и находится здесь: {self.out_file_name}')

    def sent_email(self):
        msg = MIMEMultipart()
        msg['From'] = EMAIL_FROM
        msg['To'] = ','.join(EMAIL_TO)
        msg['Date'] = formatdate(localtime=True)
        msg['Subject'] = EMAIL_SUBJECT

        msg.attach(MIMEText(EMAIL_MESSAGE))

        with open(self.out_file_name, "rb") as file:
            part = MIMEApplication(
                file.read(),
                Name=basename(self.out_file_name)
            )
        part['Content-Disposition'] = 'attachment; filename="%s"' % basename(self.out_file_name)
        msg.attach(part)

        server = smtplib.SMTP_SSL(EMAIL_SMTP_SERVER)
        server.login(EMAIL_LOGIN, EMAIL_PASSWD)
        server.sendmail(EMAIL_FROM, EMAIL_TO, msg.as_string())
        server.quit()
        print('Отчет отправлен по списку рассылки')

    def run(self):
        self.set_dates()
        self.create_report_metadata()
        self.get_banners_list()
        self.get_campaigns_list_chunks()
        self.get_banners_info_list()
        self.get_advertisers_list()
        self.add_info_to_banners_list()
        self.set_columns_order()
        self.export_to_file()
        # self.sent_email()


if __name__ == '__main__':
    # process = GetDcrReport(report_date='2024-01-01')
    process = GetDcrReport()
    process.run()
