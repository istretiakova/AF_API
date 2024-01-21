import requests
import time
import smtplib
import sys
import pandas as pd
import xml.etree.ElementTree as ET

from datetime import datetime, timedelta
from os.path import basename
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate

from settings import TOKEN

# ================ Report config =====================

TRACKERS_DATA_REPORT_ID = "6242"
REPORT_PATH = r'F:\WORK\AdFox\API_Reports\Adcampaigns'

EMAIL_SMTP_SERVER = 'mail.axkv.ru'
EMAIL_PASSWD = 'vI5ykKwkgo'
EMAIL_FROM = 'noreply@axkv.ru'

EMAIL_TO = ['itretiakova@alliance.digita']

EMAIL_MESSAGE = 'Счетчики для кампании'

EMAIL_SUBJECT = 'Supercampaign ID '

# ================ Report config end =====================

class SentTrackersToAdcampaigns():

    def __init__(self, report_date=None):
        self.report_date = datetime.now() if report_date is None else datetime.strptime(report_date, '%Y-%m-%d')
        self.date_from = ''
        self.date_to = ''
        self.trackers_folder_name = report_date.strftime("%Y-%m-%d-%H%M%S")


    def set_dates(self):
        pass

    def get_trackers_data(self):
        pass

    def get_supercampaigns_list(self):
        pass

    def create_supercampaign_trackers_list(self):
        pass

    def create_trackers_file(self):
        pass

    def create_message_metadata(self):
        pass

    def sent_file_to_adcampaigns(self):
        pass

    def create_and_sent_trackers(self):
        pass

    def run(self):
        self.set_dates()
        self.get_trackers_data()
        self.get_supercampaigns_list()






