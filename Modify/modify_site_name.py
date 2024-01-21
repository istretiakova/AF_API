import pandas as pd
import requests
import xml.etree.ElementTree as ET
from settings import TOKEN


class ModifySiteNames:

    def __init__(self, in_file=None):
        self.headers = {'Authorization': 'OAuth ' + TOKEN}
        self.url = 'https://adfox.yandex.ru/api/v1'
        self.in_file = 'upd_site_names.xlsx' if in_file is None else in_file
        self.site_names_data = pd.read_excel(self.in_file)

    def modify_site_name(self, site_id, new_site_name):
        modify_params = (
            ('object', 'website'),
            ('action', 'modify'),
            ('objectID', site_id),
            ('name', new_site_name)
        )
        response = requests.get(self.url, params=modify_params, headers=self.headers)
        root = ET.fromstring(response.text)
        code = root.find("status").find("code").text
        return code

    def modify_site_names(self):
        for idx, row in self.site_names_data.iterrows():
            code = self.modify_site_name(site_id=int(row[0]), new_site_name=row[2])
            print(row[0], row[1], row[2], code)

    def run(self):
        self.modify_site_names()


if __name__ == '__main__':
    process = ModifySiteNames(in_file='upd_site_names.xlsx')
    process.run()
