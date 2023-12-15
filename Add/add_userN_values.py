import pandas as pd
import requests
import xml.etree.ElementTree as ET
from settings import TOKEN
from utils import base_10_to_alphabet
from datetime import datetime


class AddUserNValues:

    def __init__(self, in_file=None, out_file=None, userN=59):
        self.headers = {'Authorization': 'OAuth ' + TOKEN}
        self.url = 'https://adfox.yandex.ru/api/v1'
        self.in_file = 'new_userN_values.xlsx' if in_file is None else in_file
        self.out_file = 'userN_values_{}.xlsx'.format(datetime.now().strftime("%Y-%m-%d-%H%M%S")) if out_file is None else out_file
        self.userN_values_data = pd.read_excel(self.in_file)
        self.userN = userN

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
        code = root.find("status").find("code").text
        value_id = root.find("status").find("ID").text
        return code, value_id

    def add_user_n_values(self):
        print(self.userN)
        for idx, row in self.userN_values_data.iterrows():
            code, value_id = self.add_user_n_value(value_id=row[0], value_name=row[1])
            print(row[0], row[1], code, value_id)

    def run(self):
        self.add_user_n_values()


if __name__ == '__main__':
    process = AddUserNValues(in_file='new_user60_values_05122023.xlsx', userN=60)
    process.run()
