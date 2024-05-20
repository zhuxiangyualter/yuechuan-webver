from channels.generic.websocket import AsyncWebsocketConsumer
from channels.exceptions import StopConsumer
from django.utils.timezone import now
import json
import collections

MAX_HISTORY_LENGTH = 100

history: dict[str, collections.deque] = {}

class ChatConsumer(AsyncWebsocketConsumer):
    async def websocket_connect(self, message):
        id = self.scope['url_route']['kwargs'].get('id')

        if id is None:
            id = 'base'

        await self.accept()

        await self.send(json.dumps({
            'type': 'info',
            'data': 'Connected'
        }))

        if history.get(id) is None:
            history[id] = collections.deque(maxlen=MAX_HISTORY_LENGTH)
        else:
            for i in history[id]:
                await self.send(json.dumps(i))

        await self.channel_layer.group_add(id, self.channel_name)
    
    async def websocket_receive(self, message):
        id = self.scope['url_route']['kwargs'].get('id')

        if id is None:
            id = 'base'

        raw = {
            **json.loads(message['text']),
            'time': int(now().timestamp() * 1000)
        }
        
        data = {
            'type': 'message',
            'data': json.dumps(raw)
        }

        await self.channel_layer.group_send(id, data)

        history[id].append(data)
        
    async def websocket_disconnect(self, message):
        id = self.scope['url_route']['kwargs'].get('id')

        if id is None:
            id = 'base'

        await self.channel_layer.group_discard(id, self.channel_name)
        raise StopConsumer()
    
    async def message(self, event):
        await self.send(json.dumps({
            'type': event['type'],
            'data': event['data']
        }))
    
    