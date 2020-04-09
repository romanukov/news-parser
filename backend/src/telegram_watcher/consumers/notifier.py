
from channels.generic.websocket import AsyncJsonWebsocketConsumer

class NotifierConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        usergroup = "%s.user" % str(getattr(self.user, 'pk', 'anonymous'))
        await self.channel_layer.group_add(usergroup, self.channel_name)
        await self.accept()

    # Event handler for feed.new_message event type
    async def feed_new_message(self, event):
        await self.send_json(
            {
                "action": 'feedNewMessage',
                "feed": event["feed"]
            },
        )

