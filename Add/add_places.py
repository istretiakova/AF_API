import pandas as pd
import requests
import xml.etree.ElementTree as ET
from settings import ADFOX_API_KEY
from utils import base_10_to_alphabet


class AddInventory:

    def __init__(self, in_file=None, out_file=None, block_pos_num=None):
        self.headers = {'X-Yandex-API-Key': ADFOX_API_KEY}
        self.url = 'https://adfox.yandex.ru/api/v1'
        self.in_file = 'vn_add_inventory.xlsx' if in_file is None else in_file
        self.out_file = 'vn_new_inventory.xlsx' if out_file is None else out_file
        self.block_pos_num = 6 if block_pos_num is None else block_pos_num
        self.inventory_data = pd.read_excel(self.in_file)
        self.new_sites_list = None
        self.new_sections_list = None
        self.new_places_list = None

    def create_in_sites_list(self):
        self.new_sites_list = self.inventory_data[['webmasterID', 'siteName']].drop_duplicates()

    def upd_site_info(self, site_name, site_id):
        self.inventory_data.loc[self.inventory_data['siteName'] == site_name, 'siteID'] = site_id

    def create_in_sections_list(self):
        self.new_sections_list = self.inventory_data[['siteID', 'sectionName']].drop_duplicates()

    def upd_section_info(self, section_name, site_id, section_id):
        self.inventory_data.loc[(self.inventory_data['sectionName'] == section_name) &
                                (self.inventory_data['siteID'] == site_id), 'sectionID'] = section_id

    def create_in_places_list(self):
        self.new_places_list = self.inventory_data[['siteID', 'sectionID', 'bannerTypeID',
                                                    'positionID', 'placeName']].drop_duplicates()

    def upd_place_info(self, site_id, section_id, place_id, place_name, banner_type_id, position_id):
        self.inventory_data.loc[
            (self.inventory_data['siteID'] == site_id) &
            (self.inventory_data['sectionID'] == section_id) &
            (self.inventory_data['bannerTypeID'] == banner_type_id) &
            (self.inventory_data['positionID'] == position_id) &
            (self.inventory_data['placeName'] == place_name), 'placeID'] = place_id

    def add_sites(self):
        self.create_in_sites_list()
        for index, site in self.new_sites_list.iterrows():
            add_params = (
                ('object', 'account'),
                ('action', 'add'),
                ('actionObject', 'website'),
                ('name', site['siteName']),
                ('webmasterID', site['webmasterID'])
            )
            response = requests.get(self.url, params=add_params, headers=self.headers)
            root = ET.fromstring(response.text)
            error_code = root.find("status").find("code").text
            new_site_id = root.find("status").find("ID").text
            self.upd_site_info(site['siteName'], new_site_id)
        print('Сайты созданы')

    def add_sections(self):
        self.create_in_sections_list()
        for index, section in self.new_sections_list.iterrows():
            add_params = (
                ('object', 'account'),
                ('action', 'add'),
                ('actionObject', 'zone'),
                ('name', section['sectionName']),
                ('siteID', section['siteID'])
            )
            response = requests.get(self.url, params=add_params, headers=self.headers)
            root = ET.fromstring(response.text)
            error_code = root.find("status").find("code").text
            new_section_id = root.find("status").find("ID").text
            self.upd_section_info(section['sectionName'], section['siteID'], new_section_id)
        print('Разделы созданы')

    def add_places(self):
        self.create_in_places_list()
        for index, place in self.new_places_list.iterrows():
            add_params = (
                ('object', 'account'),
                ('action', 'add'),
                ('actionObject', 'place'),
                ('name', place['placeName']),
                ('siteID', place['siteID']),
                ('zoneID', place['sectionID']),
                ('bannerTypeID', place['bannerTypeID']),
                ('positionID', place['positionID']),
                ('pct', 4)
            )
            response = requests.get(self.url, params=add_params, headers=self.headers)
            root = ET.fromstring(response.text)
            error_code = root.find("status").find("code").text
            new_place_id = root.find("status").find("ID").text

            self.upd_place_info(
                place['siteID'], place['sectionID'], new_place_id, place['placeName'],
                place['bannerTypeID'], place['positionID'])
        print('Площадки созданы')

    def add_block_positions(self):
        block_pos_df = pd.DataFrame(list(range(1, self.block_pos_num+1)), columns=['block position'])
        self.inventory_data = self.inventory_data.merge(block_pos_df, how='cross')

    def create_tags(self):
        self.inventory_data['p1'] = self.inventory_data['placeID'].apply(lambda x: base_10_to_alphabet(int(x)))
        self.inventory_data['p2'] = self.inventory_data['bannerTypeID'].apply(lambda x: base_10_to_alphabet(int(x)))
        self.inventory_data['AdFox base Tag'] = self.inventory_data.loc[:, ['p1', 'p2', 'block position']].\
            apply(lambda x: f"https://yandex.ru/ads/adfox/226279/getCode?p1={x['p1']}&p2={x['p2']}"
                            f"&puid6={x['block position']}", axis=1)
        print('Теги сформированы')

    def write_data_to_excel(self):
        self.inventory_data.to_excel(self.out_file)
        print(f'Данные записаны в файл: {self.out_file}')

    def run(self):
        self.add_sites()
        self.add_sections()
        self.add_places()
        self.add_block_positions()
        self.create_tags()
        self.write_data_to_excel()


if __name__ == '__main__':
    process = AddInventory()
    process.run()
