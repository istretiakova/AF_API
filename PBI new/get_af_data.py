# -*- coding: utf-8 -*-
"""
Created on 19.01.2024

@author: Irina Tretiakova

Получаем данные AdFox для использования в BI инструментах
"""

import requests
import pandas as pd
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
import time
from settings import TOKEN


class GetAdFoxData:

    def __init__(self):
        pass

    def create_report_task(self):
        pass

    def get_report_data(self):
        pass

    def save_report_data(self):
        pass

    def sites_list_config(self):
        pass

    def places_list_config(self):
        pass

    def banners_list_config(self):
        pass

    def supercampaigns_list_config(self):
        pass

    def campaigns_list_config(self):
        pass

    def get_list_data(self):
        pass

    def save_list_data(self):
        pass

    def run(self):
        pass


if __name__ == '__main__':
    # process = GetAdFoxData(report_date='2024-01-01')
    process = GetAdFoxData()
    process.run()
