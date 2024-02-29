import requests
import time
import pandas as pd

TOKEN = "y0_AgAAAAByRwBUAAr_jgAAAAD04Qm5-BwSIPkOQb6FoeIhgRwzK_Pe59A"
# REPORT_IDS = [('03', '6518'),  # totals
#               ('04', '6519'),  # totals
#               ('05', '6520'),  # totals
#               ('12', '6521'),  ###
#               ('13', '6522'),
#               ('14', '6523'),
#               ('15', '6524'),
#               ('16', '6525'),
#               ('17', '6526'),
#               ('18', '6527')]

date_from = '2024-02-26'
date_to = '2024-02-28'

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

report_id = '6543'

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
print(f"report state = {report_response.json()['result']['state']}")

table = report_response.json()['result']['table']
columns = report_response.json()['result']['fields']
for column_num, column_id in enumerate(columns):
    columns[column_num] = columns_names[column_id]

totals = list(report_response.json()['result']['totals'].values())

totals_list = ['Всего'] + totals

table.append(totals_list)

report_data = pd.DataFrame(data=table, columns=columns)
report_data = report_data.astype({'День': 'datetime64[ns]'})

out_file_name = r'F:\WORK\AdFox\API_Reports\Analytics\29.02.2024\6543_API.xlsx'
writer = pd.ExcelWriter(out_file_name, engine='xlsxwriter',
                        engine_kwargs={'options': {'strings_to_numbers': True,
                                                   'strings_to_urls': False}},
                        datetime_format='dd.mm.yyyy')
with writer:
    report_data.to_excel(writer, sheet_name='report', index=False)
