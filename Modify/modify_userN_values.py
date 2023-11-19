import pandas as pd
import requests
import xml.etree.ElementTree as ET
from settings import TOKEN
from utils import base_10_to_alphabet
from datetime import datetime


class ModifyUserNValues:

    def __init__(self, in_file=None, out_file=None, userN=59):
        self.headers = {'Authorization': 'OAuth ' + TOKEN}
        self.url = 'https://adfox.yandex.ru/api/v1'
        self.in_file = 'upd_userN_values.xlsx' if in_file is None else in_file
        self.out_file = 'userN_values_{}.xlsx'.format(datetime.now().strftime("%Y-%m-%d-%H%M%S")) if out_file is None else out_file
        self.userN_values_data = pd.read_excel(self.in_file)
        self.userN = userN

    def modify_user_n_value(self, object_id, value_id, value_name):
        modify_params = (
            ('object', 'userCriteria'),
            ('action', 'modifyValue'),
            ('criteriaID', self.userN),
            ('objectID', object_id),
            ('userID', value_id),
            ('name', value_name)
        )
        response = requests.get(self.url, params=modify_params, headers=self.headers)
        root = ET.fromstring(response.text)
        code = root.find("status").find("code").text
        return code

    def modify_user_n_values(self):
        print(self.userN)
        for idx, row in self.userN_values_data.iterrows():
            code = self.modify_user_n_value(object_id=int(row[0]), value_id=row[1], value_name=row[2])
            print(row[0], row[1], row[2], code)

    def run(self):
        self.modify_user_n_values()


if __name__ == '__main__':
    process = ModifyUserNValues(in_file='upd_user60_values.xlsx', userN=60)
    process.run()
