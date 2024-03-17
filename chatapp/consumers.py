import json
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Message, ChatRoom
import itertools
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

users_locations = {}

async def reset_locations_periodically():
    while True:
        await asyncio.sleep(100)
        users_locations.clear()

async def check_overlap_periodically():
    while True:
        await asyncio.sleep(40)
        for location, authors in users_locations.items():
            if len(authors) >= 2:
                combinations = list(itertools.combinations(authors, 2))
                for combination in combinations:
                    title = "_".join(sorted(combination))
                    await save_room(title)

@database_sync_to_async
def save_room(title):
    try:
        ChatRoom.objects.get(title=title)
    except ChatRoom.DoesNotExist:
        ChatRoom.objects.create(title=title)
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "chat_group",
            {
                "type": "chat.room.created",
                "title": title,
            }
        )

class ChatConsumerList(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("chat_group", self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        author, lat, long = text_data_json.get('author'), text_data_json.get('lat'), text_data_json.get('long')
        location_key = (lat, long)
        if location_key not in users_locations:
            users_locations[location_key] = [author]
        elif author not in users_locations[location_key]:
            users_locations[location_key].append(author)

    async def chat_room_created(self, event):
        title = event['title']
        await self.send(text_data=json.dumps({'title': title}))

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message, author = text_data_json['message'], text_data_json.get('author')
        room_name = self.room_name
        await self.save_message(message, author, room_name)
        await self.channel_layer.group_send(self.room_group_name, {"type": "chat_message", "message": message, "author": author, "room_name": self.room_name})

    @database_sync_to_async
    def save_message(self, message, author, room_name):
        room = ChatRoom.objects.get(title=room_name)
        Message.objects.create(content=message, author=author, room=room)

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({"message": event['message'], "author": event['author'], "room_name": event['room_name']}))
