from decorators.extras import getAlladmins
from decorators.message_factory import getMessage
from typing import Callable
from pyrogram import Client
from pyrogram.filters import private_filter
from pyrogram.types import Message, CallbackQuery
from bson import json_util
from utils import config, mongoDBClient, logException


def save_user_chat_in_db(func: Callable) -> Callable:
    async def decorator(client: Client, incomingPayload):
        try:
            from_user = incomingPayload.from_user

            if isinstance(incomingPayload, CallbackQuery) is True:
                message: Message = incomingPayload.message
            else:
                message: Message = incomingPayload

            current_chat = message.chat
            current_client = None
            is_private = await private_filter(None, None, message) is True
            # if this is a private message then add to tgcalls_users
            if is_private is True:
                document = {
                    "chat_id": current_chat.id,
                    "type": "private",
                    "username": current_chat.username
                    if hasattr(current_chat, "username")
                    else "",
                    "first_name": current_chat.first_name
                    if hasattr(current_chat, "first_name")
                    else "",
                    "last_name": current_chat.last_name
                    if hasattr(current_chat, "last_name")
                    else "",
                    "is_private": is_private,
                }
                current_client = mongoDBClient.add_tgcalls_users(
                    current_chat.id, json_util.dumps(document)
                )
            else:
                current_client = {
                    "chat_id": current_chat.id,
                    "type": current_chat.type,
                    "username": current_chat.username
                    if hasattr(current_chat, "username")
                    else "",
                    "title": current_chat.title
                    if hasattr(current_chat, "title")
                    else "",
                    "permissions": {},
                    "admins": await getAlladmins(client, current_chat.id),
                    "active": int(config.get("ALLOW_MULTIPLE_CHATS")) == 1,
                    "error": "",
                    "remove_messages": -1,
                    "userBot": [],
                    "extras": {
                        "min_members": int(config.get("MIN_MEMBERS_REQUIRED")),
                        "allow_video": False,
                        "allow_audio": True,
                        "allow_youtube": True,
                        "allow_others": False,
                        "max_video_res": 360,
                        "max_audio_res": 150,
                        "max_duration": int(config.get("ALLOWED_SONG_DURATION_IN_SEC")),
                        "max_queue_size": int(config.get("PLAYLIST_SIZE")),
                        "allow_repeat": False,
                    },
                }
                # if user is running in no_mongo mode set userbot info and allow all restricted features
                if not mongoDBClient.client:
                    current_client["extras"]["allow_video"] = True
                    current_client["extras"]["allow_others"] = True
                    current_client["extras"]["max_video_res"] = 1920
                    current_client["extras"]["max_video_res"] = 1000
                    current_client["extras"]["allow_repeat"] = True
                    current_client["userBot"] = [
                        {
                            "apiId": config.get("API_ID"),
                            "apiHash": config.get("API_HASH"),
                            "sessionId": config.get("USERBOT_SESSION"),
                        }
                    ]
                current_client = mongoDBClient.add_tgcalls_chats(
                    current_chat.id, json_util.dumps(current_client)
                )
                is_admin = from_user is not None and any(
                    user["chat_id"] == from_user.id for user in current_client["admins"]
                )
                current_client["is_admin"] = is_admin is True
                if (
                    current_client.get("userBot")
                    and isinstance(current_client.get("userBot"), list)
                    and len(current_client.get("userBot")) > 0
                ):
                    current_client["userBot"] = (current_client["userBot"])[-1]

            current_client["from_user"] = from_user
            current_client["from_chat"] = current_chat
            current_client["is_private"] = is_private

            return await func(client, incomingPayload, current_client)
        except Exception as ex:
            logException(f"Error in save_user_chat_in_db: {ex}")

    return decorator
