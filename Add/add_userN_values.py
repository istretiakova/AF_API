import pandas as pd
import requests
import xml.etree.ElementTree as ET
from settings import ADFOX_API_KEY
from utils import base_10_to_alphabet
from datetime import datetime


class AddUserNValues:

    def __init__(self, in_file=None, out_file=None, userN=59):
        self.headers = {'X-Yandex-API-Key': ADFOX_API_KEY}
        self.url = 'https://adfox.yandex.ru/api/v1'
        self.in_file = 'new_userN_values.xlsx' if in_file is None else in_file
        self.out_file = 'userN_values_{}.xlsx'.format(datetime.now().strftime("%Y-%m-%d-%H%M%S")) if out_file is None else out_file
        self.userN_values_data = pd.read_excel(self.in_file)
        self.userN = userN
        self.new_userN_values_list = pd.read_excel(self.in_file)

    def add_user_n_value(self, value_id, value_name):
        add_params = (
            ('object', 'userCriteria'),
            ('action', 'addValue'),
            ('criteriaID', self.userN),
            ('userID', value_id),
            ('name', value_name)
        )
        response = requests.get(self.url, params=add_params, headers=self.headers)
        root = ET.fromstring(response.text)
        error_code = root.find("status").find("code").text
        new_value_id = root.find("status").find("ID").text

    def add_user_n_values(self):
        for value_id in self.userN_values_data['ID']:
            self.add_user_n_value(value_id=value_id, value_name=value_id)
            print(value_id)

    def run(self):
        self.add_user_n_values()


if __name__ == '__main__':
    process = AddUserNValues(in_file='new_user60_values.xlsx', userN=60)
    process.run()
