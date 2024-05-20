import hashlib
import hmac
import base64
import json
import requests
import time
from django.core.files.base import ContentFile

from .models import *

from user.models import User

class SlidesAPI:

    def __init__(self, APPID: str, APISecret: str, APIKey: str):
        self.APPID = APPID
        self.APISecret = APISecret
        self.APIKey = APIKey

    def sign(self, timestamp: str):
        auth = hashlib.md5((self.APPID + timestamp).encode()).hexdigest()
        signature = base64.b64encode(hmac.new(self.APISecret.encode(), auth.encode(), hashlib.sha1).digest()).decode()
        return signature
    
    def get_session(self, timestamp: int):
        session = requests.Session()
        signature = self.sign(str(timestamp))

        session.headers = {
            "appId": self.APPID,
            "timestamp": str(timestamp),
            "signature": signature,
            "Content-Type":"application/json; charset=utf-8"
        }
        return session
    
    def create_task(self, description: str, creator: User) -> SlideGeneration | None:
        url = 'https://zwapi.xfyun.cn/api/aippt/create'
        session = self.get_session(int(time.time()))

        data = {
            "query": description,
            "author": 'AILearn',
        }

        try:
            response = session.post(url, data=json.dumps(data))
            data = json.loads(response.text)

            if data['code'] != 0:
                return None
            
            cover = session.get(data['data']['coverImgSrc'])
            ext = data['data']['coverImgSrc'].split('.')[-1]
        except requests.RequestException:
            return None
        
        task = SlideGeneration.objects.create(
            prompt = description,
            remote_id = data['data']['sid'],
            title = data['data']['title'],
            subtitle = data['data']['subTitle'],
            creator = creator
        )

        task.cover = ContentFile(cover.content, name='cover.' + ext)
        task.save()

        return task
    
    def fetch(self, record: SlideGeneration) -> bool:
        if record.status == 'complete':
            return True
        
        timestamp = str(int(time.time()))
        signature = self.sign(timestamp)

        session = requests.Session()

        session.headers = {
            "appId": self.APPID,
            "timestamp": timestamp,
            "signature": signature,
            "Content-Type":"application/json; charset=utf-8"
        }

        try:
            response = session.get('https://zwapi.xfyun.cn/api/aippt/progress?sid=' + record.remote_id)
            data = json.loads(response.text)

            if data['data']['process'] == 100:
                result = data['data']['pptUrl']
                slide = session.get(result)
                
                record.result = ContentFile(slide.content, 'temp.pptx')
                record.status = 'complete'

                record.save()
                
                return True
            else:
                return False
            
        except requests.RequestException:
            return False