import json

import aioredis
from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.conf import settings
from django.core import serializers

from app_user.models import User


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]

        try:
            self.partner = await self.get_partner(self.room_name)
        except User.DoesNotExist:
            await self.close()
        await self.channel_layer.group_add(self.room_name, self.channel_name)
        await self.update_user_status(self.user, self.partner, is_online=True)
        await self.channel_layer.group_send(
            self.room_name,
            {
                "type": "notification",
                "notification": f"{self.user.get_full_name()} has joined the chat",
                "notification_type": "connection",
                "user": await self.get_user_details(self.user),
            },
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_send(
            self.room_name,
            {
                "type": "notification",
                "notification": f"{self.user.get_full_name()} has left the chat",
                "notification_type": "disconnection",
                "user": await self.get_user_details(self.user),
            },
        )
        await self.channel_layer.group_discard(self.room_name, self.channel_name)
        await self.update_user_status(self.user, None)
        await self.close()

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        if text_data_json.get("message"):
            message = text_data_json["message"]
            await self.channel_layer.group_send(
                self.room_name,
                {
                    "type": "chat",
                    "message": message,
                    "message_type": "text_message",
                    "user": await self.get_user_details(self.user),
                },
            )

    async def chat(self, event):
        message = event["message"]
        message_type = event.get("message_type")
        user = event.get("user")
        await self.send(
            text_data=json.dumps(
                {"message": message, "user": user, "message_type": message_type}
            )
        )

    async def notification(self, event):
        notification = event["notification"]
        notification_type = event.get("notification_type")
        user = event.get("user")
        await self.send(
            text_data=json.dumps(
                {
                    "notification": notification,
                    "user": user,
                    "notification_type": notification_type,
                }
            )
        )

    @sync_to_async
    def update_user_status(self, user, connected_user=None, **kwargs):
        if kwargs.get("is_online") is not None:
            user.is_online = kwargs.get("is_online")
        if connected_user is None:
            if user.current_connection is not None:
                user.current_connection.current_connection = None
                user.current_connection.save()
        user.current_connection = connected_user
        user.save()

    @sync_to_async
    def get_partner(self, room_name):
        partner_id = (
            room_name.split("_")[2]
            if self.user.id == int(room_name.split("_")[1])
            else room_name.split("_")[1]
        )
        return User.objects.get(id=partner_id)

    @sync_to_async
    def get_user_details(self, user):
        fields = (
            "gender",
            "country",
            "first_name",
            "last_name",
        )
        result = serializers.serialize("json", [user], fields=fields)[1:-1]
        result = json.loads(result)
        result["fields"]["id"] = result["pk"]
        return result["fields"]


class FindConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        self.redis = await aioredis.from_url(f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}")
        await self.redis.set(f"user:{self.user.id}", self.channel_name)
        await self.update_user_status(self.user, None)
        await self.accept()

    async def disconnect(self, close_code):
        await self.redis.delete(f"user:{self.user.id}")
        await self.redis.close()

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        action = text_data_json.get("action")

        if action == "find_match":
            await self.initiate_matching_process()

    async def initiate_matching_process(self):
        await self.update_user_status(self.user, None, is_online=True)
        connected_user_ids = await self.redis.keys("user:*")
        connected_user_ids = [int(user_id.decode("utf-8").split(":")[1]) for user_id in connected_user_ids]
        matched_user = await self.find_match(self.user, connected_user_ids)
        # print(matched_user)
        if matched_user:
            room_name = f"chat_{self.user.id}_{matched_user.id}"
            print(room_name)
            await self.notify_user_of_room(self.user, room_name)
            await self.notify_user_of_room(matched_user, room_name)
        else:
            await self.send(text_data=json.dumps({"error": "No match found"}))

    async def notify_user_of_room(self, user, room_name):
        channel_name = await self.redis.get(f"user:{user.id}")
        channel_name = channel_name.decode("utf-8") if channel_name else None
        if channel_name:
            await self.channel_layer.send(
                channel_name, {"type": "room_notification", "room_name": room_name}
            )

    async def room_notification(self, event):
        room_name = event.get("room_name")
        await self.send(
            text_data=json.dumps(
                {
                    "room_name": room_name,
                }
            )
        )

    @sync_to_async
    def find_match(self, user, connected_user_ids):
        if user.current_connection is not None:
            return None

        interests = user.interests.all()
        potential_matches = User.objects.filter(
            is_online=True, interests__in=interests, current_connection=None
        ).exclude(id=user.id)

        for potential_match in potential_matches:
            if potential_match.id in connected_user_ids:
                return potential_match
        any_online_user = (
            User.objects.exclude(id=user.id)
            .filter(
                id__in=connected_user_ids,
                is_online=True,
                current_connection=None,
            )
            .first()
        )
        return any_online_user

    @sync_to_async
    def update_user_status(self, user, connected_user=None, **kwargs):
        if kwargs.get("is_online") is not None:
            user.is_online = kwargs.get("is_online")
        if connected_user is None:
            if user.current_connection is not None:
                user.current_connection.current_connection = None
                user.current_connection.save()
        user.current_connection = connected_user
        user.save()
