import requests
from settings import TOKEN
import xml.etree.ElementTree as ET


file_name = 'https://vi.cdnvideo.ru/media/m/test/adfox/api_file_upload/test_video.mp4'
campaign_id = '2683083'

headers = {'Authorization': 'OAuth ' + TOKEN}
url = 'https://adfox.yandex.ru/api/v1'

params = (
            ('object', 'campaign'),
            ('action', 'upload'),
            ('actionObject', 'URL'),
            ('objectID', campaign_id),
            ('URL', file_name)
)


response = requests.get(url, params=params, headers=headers)
root = ET.fromstring(response.text)