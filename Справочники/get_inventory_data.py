import pandas as pd
import xml.etree.ElementTree as ET
import requests
from datetime import datetime
from settings import ADFOX_API_KEY
from utils import base_10_to_alphabet


class GetInventoryData:

    def __init__(self):
        self.headers = {'X-Yandex-API-Key': ADFOX_API_KEY}
        self.url = 'https://adfox.yandex.ru/api/v1'
        self.limit = 1000
        self.offset = 0
        self.total_rows = self.limit + 1
        self.total_pages = None
        self.page = 0
        self.rows = 0
        self.params = (
            ('object', 'account'),
            ('action', 'list'),
            ('offset', self.offset),
            ('limit', self.limit),
            ('encoding', 'UTF-8')
        )
        self.request_data = None

    def upd_params(self, extra_params):
        self.params += extra_params

    def send_request(self):
        response = requests.get(self.url, params=self.params, headers=self.headers)
        root = ET.fromstring(response.text)
        self.total_pages = int(root.find('result').find('total_pages').text)
        self.page = int(root.find('result').find('page').text)
        self.total_rows = int(root.find('result').find('total_rows').text)
        self.rows = int(root.find('result').find('rows').text)
        self.request_data = root.find("result").find("data")

    def get_sites_list(self):
        pass