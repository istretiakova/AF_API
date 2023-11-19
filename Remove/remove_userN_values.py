import pandas as pd
import requests
from settings import TOKEN


class AddUserNValues:

    def __init__(self, in_file=None):
        self.headers = {'Authorization': 'OAuth ' + TOKEN}
        self.url = 'https://adfox.yandex.ru/api/v1'
        self.in_file = '' if in_file is None else in_file
        self.userN_values_data = pd.read_excel(self.in_file)

    def remove_user_n_value(self, value_id):
        add_params = (
            ('object', 'userCriteria'),
            ('action', 'removeValue'),
            ('objectID', value_id),
        )
        requests.get(self.url, params=add_params, headers=self.headers)

    def remove_user_n_values(self):
        for value_id in self.userN_values_data['ID']:
            self.remove_user_n_value(value_id=value_id)
            print(value_id)

    def run(self):
        self.remove_user_n_values()


if __name__ == '__main__':
    process = AddUserNValues(in_file='DA_user_criteria28_values_2023-10-26-144846.xlsx')
    process.run()
