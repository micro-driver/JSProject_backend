from channels.generic.websocket import AsyncWebsocketConsumer
import json
from django.conf import settings
from django.core.cache import cache

from thrift import Thrift
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol

from match_system.src.match_server.match_service import Match
from game.models.player.player import Player
from channels.db import database_sync_to_async
class MultiPlayer(AsyncWebsocketConsumer):
    async def connect(self):
        # self.room_name = None
        # for i in range(1000):
        #     name = "room-%d" % (i)
        #     if not cache.has_key(name) or len(cache.get(name)) < settings.ROOM_CAPACITY:
        #         self.room_name = name
        #         break
        # if not self.room_name:
        #     return
        await self.accept()
        # if not cache.has_key(self.room_name):
        #     cache.set(self.room_name, [], 3600)
        # for player in cache.get(self.room_name):
        #     await self.send(text_data=json.dumps({
        #         'event': "create_player",
        #         'uuid': player['uuid'],
        #         'username': player['username'],
        #         'img_id': player['img_id'],
        #     }))
        # await self.channel_layer.group_add(self.room_name, self.channel_name)

    async def disconnect(self, close_code):
        print('Disconnect')
        await self.channel_layer.group_discard(self.room_name, self.channel_name)

    async def create_player(self, data):
        # players = cache.get(self.room_name)
        # players.append({
        #     'uuid': data['uuid'],
        #     'username': data['username'],
        #     'img_id': data['img_id']
        # })
        # cache.set(self.room_name, players, 3600)  # 有效期1小时
        # await self.channel_layer.group_send(
        #     self.room_name,
        #     {
        #         'type': "group_send_event",
        #         'event': "create_player",
        #         'uuid': data['uuid'],
        #         'username': data['username'],
        #         'img_id': data['img_id'],
        #     }
        # )
        self.room_name=None
        self.uuid=data['uuid']
        # Make socket
        transport = TSocket.TSocket('127.0.0.1', 9090)

        # Buffering is critical. Raw sockets are very slow
        transport = TTransport.TBufferedTransport(transport)

        # Wrap in a protocol
        protocol = TBinaryProtocol.TBinaryProtocol(transport)

        # Create a client to use the protocol encoder
        client = Match.Client(protocol)

        # Connect!
        transport.open()

        def db_get_player():
            player = Player.objects.get(user__username=data['username'])
            return player
        player = await database_sync_to_async(db_get_player)()
        client.add_player(player.score,data['uuid'],data['username'],str(data['img_id']),self.channel_name)

        transport.close()

    async def move_to(self, data):
        await self.channel_layer.group_send(
            self.room_name,
            {
                'type': "group_send_event",
                'event': "move_to",
                'uuid': data['uuid'],
                'tx': data['tx'],
                'ty': data['ty'],
            }
        )

    async def shoot_fireball(self, data):
        await self.channel_layer.group_send(
            self.room_name,
            {
                'type': "group_send_event",
                'event': "shoot_fireball",
                'uuid': data['uuid'],
                'tx': data['tx'],
                'ty': data['ty'],
                'ball_uuid': data['ball_uuid'],
            }
        )

    async def send_message(self, data):
        await self.channel_layer.group_send(
            self.room_name,
            {
                'type': "group_send_event",
                'event': "send_message",
                'uuid': data['uuid'],
                'username': data['username'],
                'text': data['text'],
            }
        )

    async def group_send_event(self, data):
        # if not self.room_name: 因为没用cache没有使用redis而是用LocMemCache，没有keys方法
        #     keys=cache.keys('*%s*' % (self.uuid))
        #     if keys:
        #         self.room_name=keys[0]
        if data['event'] == "send_room_name":
            self.room_name = data['room_name']
        else:
            await self.send(text_data=json.dumps(data))

    async def receive(self, text_data):
        data = json.loads(text_data)
        event = data['event']
        if event == "create_player":
            await self.create_player(data)
        if event == "move_to":
            await self.move_to(data)
        if event == "shoot_fireball":
            await self.shoot_fireball(data)
        if event == "send_message":
            await self.send_message(data)






