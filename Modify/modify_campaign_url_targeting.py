import pandas as pd
import xml.etree.ElementTree as ET
import requests
from datetime import datetime

from settings import TOKEN

headers = {'Authorization': 'OAuth ' + TOKEN}
url = 'https://adfox.yandex.ru/api/v1'