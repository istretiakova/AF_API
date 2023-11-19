import requests
import pandas as pd
import xml.etree.ElementTree as ET
from datetime import datetime
import time
from settings import TOKEN


class GetDcrReport:

    def __init__(self):
        self.current_date = datetime.now()
        self.date_from = f'{self.current_date.year}-{self.current_date.month}-01'
        self.date_to = f'{self.current_date.year}-{self.current_date.month}-{self.current_date.day}'
        self.out_file_name = r'F:\WORK\AdFox\API_Reports\DCR\dcr-report_01-{}.xlsx'. \
            format(datetime.now().strftime("%d.%m.%Y-%H%M%S"))
        self.campaigns_list_chunks = []
        self.banners_chunk = 0
        self.banners_info_rows = []
        self.banners_info = pd.DataFrame()
        self.report_header = []
        self.banners_list = pd.DataFrame()
        print(f'this_month = {self.current_date.year}-{self.current_date.month}')
        print(f'prev_month = {self.current_date.year}-{self.current_date.month - 1}')

    def get_banners_list(self):
        print('Получаем список баннеров текущего месяца get_banners_impressions(self)')
        report_id = '5933'
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
    def check_erid_error(media_url, click_url, erid):
        pass

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

    def add_info_to_banners_list(self):
        print('\r\nОбъединяем списко баннеров с инфо о баннерах add_info_to_banners_list(self)')
        self.banners_list = self.banners_list.merge(self.banners_info, how='left',
                                                    left_on='bannerId', right_on='ID')
        self.banners_list['status'] = self.banners_list['status'].apply(lambda x: self.get_status_name(x))
        self.banners_list['Verifier'] = self.banners_list['parameter1'].apply(lambda x: self.get_verifier(x))
        self.banners_list['Admon'] = self.banners_list['templateName'].apply(lambda x: self.get_admon_state(x))
        self.banners_list['Mediaplan ID'] = self.banners_list['campaignName'].apply(lambda x: self.get_mediaplan_id(x))

    def set_columns_order(self):
        print('\r\nОставляем только нужные колонки и переименовываем их set_columns_order(self)')
        fields = {'bannerId': 'Banner ID',
                  'name': 'Banner Name',
                  'campaignID': 'Campaign ID',
                  'campaignName': 'Campaign Name',
                  'Mediaplan ID': 'Mediaplan ID',
                  'loadsCommercial': 'Loads',
                  'impressionsCommercial': 'Impressions',
                  'Verifier': 'Verifier',
                  'Admon': 'Admon',
                  'parameter3': 'ERID',
                  'parameter4': 'Duration',
                  'parameter24': 'skipTime',
                  'status': 'status',
                  'templateName': 'Template Name',
                  'parameter1': 'Media URL',
                  'parameter2': 'Click URL',
                  'parameter7': 'URLMOD final',
                  'parameter9': 'impression1',
                  'parameter10': 'impression2',
                  'parameter11': 'impression3',
                  'parameter12': 'impression4',
                  'dateAdded': 'Banner dateAdded',
                  'dateStart': 'Banner dateStart',
                  'dateEnd': 'Banner dateEnd',
                  'campaignDateStart': 'Campaign dateStart',
                  'campaignDateEnd': 'Campaign dateEnd'}
        self.banners_list = self.banners_list[fields.keys()]
        self.banners_list = self.banners_list.rename(columns=fields)
        print(self.banners_list.info())

    def create_report_header(self):
        print('Формируем шапку для отчета create_report_header(self)')
        build_on = f'{self.current_date.day}.{self.current_date.month}.{self.current_date.year}'
        date_from = f'01.{self.current_date.month}.{self.current_date.year}'
        date_to = f'{self.current_date.day - 1}.{self.current_date.month}.{self.current_date.year}'
        self.report_header = [
            ['Report name', 'Ежедневный отчет по креативам'],
            ['Build on', build_on],
            ['Date from', date_from],
            ['Date to', date_to]
        ]

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

            thin_cols_list = [0, 2, 4, 5, 6, 7, 8, 9, 10, 11, 12, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25]
            wide_cols_list = [1, 3, 13, 14, 15]

            for col in thin_cols_list:
                worksheet.set_column(col, col, 12)

            for col in wide_cols_list:
                worksheet.set_column(col, col, 40)

        print(f'Отчет готов и находится здесь: {self.out_file_name}')

    def run(self):
        self.create_report_header()
        self.get_banners_list()
        self.get_campaigns_list_chunks()
        self.get_banners_info_list()
        self.add_info_to_banners_list()
        self.set_columns_order()
        self.export_to_file()


if __name__ == '__main__':
    process = GetDcrReport()
    process.run()
