# -*- coding: utf-8 -*-
"""
Created on Fri Feb 03 13:40:05 2023

@author: Irina Tretiakova

Получаем справочник ГЕО

"""

import pandas as pd
import xml.etree.ElementTree as ET
import requests
from datetime import datetime
from settings import TOKEN

file_name = r'F:\WORK\AdFox\API_Reports\19.09.2023\DA_geo_list_{}.xlsx'.format(datetime.now().strftime("%Y-%m-%d-%H%M%S"))
geo_data = r'F:\WORK\AdFox\API_Reports\19.09.2023\geoBaseTree.xml'

tree = ET.parse(geo_data)
root = tree.getroot()
data = root.find("result").find("data")

indent = 0
geo_data_list = []
next_parent_id = None
next_parent_name = None

def get_geo_data_recur(data, parent_id=None, parent_name=None):
    global geo_data_list
    global indent

    for row in data:
        geo_data_dict = {'id0': None, 'name0': None,
                         'id1': None, 'name1': None,
                         'id2': None, 'name2': None,
                         'id3': None, 'name3': None,
                         'id4': None, 'name4': None,
                         'id5': None, 'name5': None}
        for child in list(row):
            if child.tag == 'id':
                next_parent_id = child.text
            if child.tag == 'name':
                next_parent_name = child.text
            if child.tag == 'children':
                indent += 1
                get_geo_data_recur(child, parent_id=next_parent_id, parent_name=next_parent_name)
                indent -= 1
            geo_data_dict[child.tag + str(indent)] = child.text
            if indent > 0:
                geo_data_dict['id' + str(indent-1)] = parent_id
                geo_data_dict['name' + str(indent-1)] = parent_name
        print(geo_data_dict)
        geo_data_list.append(geo_data_dict)
    return geo_data_list


geo_data = pd.DataFrame(get_geo_data_recur(data))
#geo_data = geo_data.fillna(method='bfill')
print(geo_data)
geo_data.to_excel(file_name)

print('Отчет готов и находится здесь: {}'.format(file_name))
