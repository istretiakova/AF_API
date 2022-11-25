# -*- coding: utf-8 -*-
"""
Created on Fri Sep 02 10:23:54 2022

@author: Irina Tretiakova

Получаем данные о кампаниях с соц-дем таргетингом по месяцам

"""

import pandas as pd
import xml.etree.ElementTree as ET
import requests
from datetime import datetime
from settings import ADFOX_API_KEY
import os

# ===== Начало конфига параметров отчета =====
DDR_folder = r'F:\WORK\Mediascope\Мониторинг попадания в ЦА\DDR'

"""
F:\WORK\Mediascope\Мониторинг попадания в ЦА\DDR\ddr-report-20220201-VideoNet.xls
F:\WORK\Mediascope\Мониторинг попадания в ЦА\DDR\ddr-report-20220301-VideoNet.xls
F:\WORK\Mediascope\Мониторинг попадания в ЦА\DDR\ddr-report-20220401-VideoNet.xls
F:\WORK\Mediascope\Мониторинг попадания в ЦА\DDR\ddr-report-20220501-VideoNet.xls
F:\WORK\Mediascope\Мониторинг попадания в ЦА\DDR\ddr-report-20220601-VideoNet.xls
F:\WORK\Mediascope\Мониторинг попадания в ЦА\DDR\ddr-report-20220701-VideoNet.xls
F:\WORK\Mediascope\Мониторинг попадания в ЦА\DDR\ddr-report-20220801-VideoNet.xls
F:\WORK\Mediascope\Мониторинг попадания в ЦА\DDR\ddr-report-20220901-VideoNet.xls
"""






def parse_ddr(ddr_file):
    """
    Разбираем отчет DDR, формируем csv со списком ID
    :param ddr_file:
    :return:
    """
    pass


def check_new_ddr(folder):
    """
    Проверяем наличие новых DDR отчетов
    :param folder:
    :return:
    """
    pass


def create_campaigns_lists(folder):
    """
    Из файлов с DDR отчетами формируем списки ID кампаний по месяцам
    """
    for dirpath, dirnames, filenames in os.walk(folder):
        for file in filenames:
            full_file_path = os.path.join(dirpath, file)
            print(full_file_path)


# create_campaigns_lists(folder=DDR_folder)


