import json
from channels.generic.websocket import AsyncWebsocketConsumer

class PredictionConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for real-time prediction updates.
    """

    async def connect(self):
        """
        Handle WebSocket connection.
        """
        self.user_id = self.scope['url_route']['kwargs']['user_id']
        self.group_name = f"user_{self.user_id}"

        # Join a group for the user
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        """
        Handle WebSocket disconnection.
        """
        # Leave the group
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        """
        Handle incoming WebSocket messages.
        """
        data = json.loads(text_data)
        message = data.get('message')

        # Send the message to the group
        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'send_update',
                'message': message
            }
        )

    async def send_update(self, event):
        """
        Send updates to the WebSocket client.
        """
        message = event['message']

        # Send the message to the WebSocket
        await self.send(text_data=json.dumps({
            'message': message
        }))