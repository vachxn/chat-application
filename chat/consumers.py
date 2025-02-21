import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from .models import Thread, ChatMessage

User = get_user_model()


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """Handles WebSocket connection"""
        user = self.scope['user']
        if not user.is_authenticated:
            await self.close()
            return

        self.chat_room = f'user_chatroom_{user.id}'

        await self.channel_layer.group_add(
            self.chat_room,
            self.channel_name
        )

        await self.accept()

    async def receive(self, text_data):
        """Handles messages received from WebSocket"""
        try:
            received_data = json.loads(text_data)
            msg = received_data.get('message')
            sent_by_id = received_data.get('sent_by')
            send_to_id = received_data.get('send_to')
            thread_id = received_data.get('thread_id')

            if not msg:
                print('Error: Empty message')
                return

            sent_by_user = await self.get_user_object(sent_by_id)
            send_to_user = await self.get_user_object(send_to_id)
            thread_obj = await self.get_thread(thread_id)

            if not sent_by_user or not send_to_user or not thread_obj:
                print('Error: Invalid user or thread')
                return

            # Create and save the message
            chat_message = await self.create_chat_message(thread_obj, sent_by_user, msg)

            response = {
                'message': chat_message.message,
                'sent_by': sent_by_user.id,
                'thread_id': thread_obj.id,
            }

            other_user_chat_room = f'user_chatroom_{send_to_id}'

            # Send message to both users in the chat
            await self.channel_layer.group_send(
                other_user_chat_room,
                {
                    'type': 'chat.message',
                    'text': json.dumps(response)
                }
            )

            await self.channel_layer.group_send(
                self.chat_room,
                {
                    'type': 'chat.message',
                    'text': json.dumps(response)
                }
            )

        except json.JSONDecodeError:
            print("Error: Invalid JSON data received")

    async def disconnect(self, close_code):
        """Handles WebSocket disconnection"""
        user = self.scope['user']
        if user.is_authenticated:
            await self.channel_layer.group_discard(
                self.chat_room,
                self.channel_name
            )

    async def chat_message(self, event):
        """Handles message sending"""
        await self.send(text_data=event['text'])

    @database_sync_to_async
    def get_user_object(self, user_id):
        """Fetches user object asynchronously"""
        return User.objects.filter(id=user_id).first()

    @database_sync_to_async
    def get_thread(self, thread_id):
        """Fetches thread object asynchronously"""
        return Thread.objects.filter(id=thread_id).first()

    @database_sync_to_async
    def create_chat_message(self, thread, user, msg):
        """Creates a new chat message asynchronously"""
        return ChatMessage.objects.create(thread=thread, user=user, message=msg)
