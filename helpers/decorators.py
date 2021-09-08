import asyncio
from typing import Callable
from bson import json_util
from pyrogram import Client
from pyrogram.types import Message
from utils.Logger import *
from utils.Config import Config
from utils.MongoClient import MongoDBClient
from utils.Helper import Helper
from helpers.fromatMessages import getMessage
import re

config = Config()
MongoDBClient = MongoDBClient()
helper = Helper()


def errors(func: Callable) -> Callable:
    async def decorator(client: Client, message: Message):
        try:
            return await func(client, message)
        except Exception as e:
            await message.reply(f"{type(e).__name__}: {e}")

    return decorator


def hasRequiredPermission(user):
    try:
        required = [
            "can_post_messages",
            "can_edit_messages",
            "can_invite_users",
            "can_delete_messages",
            "can_manage_voice_chats",
            "can_promote_members",
        ]
        not_present = []
        for _ in required:
            if hasattr(user, _) is not True or user[_] is False:
                not_present.append(_)
        return len(not_present) == 0
    except Exception as ex:
        logWarning(f"Error while checking for required permission : {ex}")
        return False


def parsePlayCommand(command, is_admin=False):
    is_video = helper.checkForArguments(command, "IS_VIDEO")
    resolution = helper.checkForArguments(command, "RES")
    if resolution is None:
        resolution = 128 if is_video is False else 480
    song_name = helper.checkForArguments(command, "NAME")
    is_repeat = helper.checkForArguments(command, "REPEAT")
    is_silent = helper.checkForArguments(command, "SILENT")
    only_audio = helper.checkForArguments(command, "ONLY_AUDIO")
    lip_sync = helper.checkForArguments(command, "LIP_SYNC")
    _urls = helper.getUrls(song_name)
    is_url = len(_urls) > 0
    song_url = _urls[0] if is_url is True else None
    is_youtube = (
        True
        if (
            is_url is False
            or (
                is_url is True
                and re.search("youtube\.|youtu\.be|youtube-nocookie\.", song_url)
            )
        )
        else False
    )

    return {
        "is_video": is_video,
        "resolution": resolution,
        "is_youtube": is_youtube,
        "is_url": is_url,
        "song_url": song_url,
        "song_name": song_name,
        "is_repeat": is_repeat is True,
        "is_silent": is_silent is True and is_admin is True,
        "only_audio": only_audio is True,
        "lip_sync": lip_sync is True,
    }


async def delayDelete(message, delay=1):
    try:
        await asyncio.sleep(delay)
        await message.delete()
    except Exception as ex:
        logException("Error while deleteing message : {message} , {ex}", True)


async def send_message(client, chat_id, message, is_silent):
    if is_silent is True:
        return None
    return await client.send_message(chat_id, message)


async def edit_sent_message(sent_message, message, is_silent):
    if sent_message is None or is_silent is True:
        return None
    return await sent_message.edit(message)


def chat_allowed(func: Callable) -> Callable:
    async def decorator(client: Client, message: Message):
        try:
            ALLOWED_CHAT_TYPES = config.get("ALLOWED_CHAT_TYPES")
            current_client = config.fetchClient(message.chat.id)

            # if the user is from a disallowed chat type show error message
            if message.chat.type not in ALLOWED_CHAT_TYPES:
                logInfo(
                    f"user not allowed to perform action in chat : {message.chat.id} , {message.chat.type}"
                )

                # if this is a private message then add to database
                if message.chat and message.chat.type == "private":
                    document = {
                        "chat_id": message.chat.id,
                        "type": "private",
                        "username": message.chat.username
                        if hasattr(message.chat, "username")
                        else "",
                        "first_name": message.chat.first_name
                        if hasattr(message.chat, "first_name")
                        else "",
                        "last_name": message.chat.last_name
                        if hasattr(message.chat, "last_name")
                        else "",
                        "updated_at": datetime.now(),
                    }
                    if MongoDBClient.client is not None:
                        MongoDBClient.add_tgcalls_users(document)
                msg, kbd = getMessage(message, "private-chat")
                return await client.send_message(
                    message.chat.id,
                    f"{msg}",
                    disable_web_page_preview=True,
                    reply_markup=kbd,
                )

            # if database url is not present then simply return the current chat as client
            if MongoDBClient.client is None:
                current_client = {
                    "chat_id": message.chat.id,
                    "type": message.chat.type,
                    "username": message.chat.username
                    if hasattr(message.chat, "username")
                    else "",
                    "title": message.chat.title
                    if hasattr(message.chat, "title")
                    else "",
                    "permissions": {},
                    "updated_at": datetime.now(),
                    "admins": [],
                    "active": True,
                    "remove_messages": -1,
                    "admin_mode": False,
                }
            elif current_client in [None, []]:
                logInfo(f"Adding a new client in db => {message.chat.id}")
                state_value = True
                # if the service is running in single mode , check if there are any active clients , if yes restrict the chat from proceeding
                # if not add the chat and allow it
                if (
                    config.get("MODE") == "single"
                    and len(
                        list(
                            filter(
                                lambda c: c.get("active") is True,
                                config.get("ACTIVE_CLIENTS"),
                            )
                        )
                    )
                    > 0
                ):
                    state_value = False

                document = {
                    "chat_id": message.chat.id,
                    "type": message.chat.type,
                    "username": message.chat.username
                    if hasattr(message.chat, "username")
                    else "",
                    "title": message.chat.title
                    if hasattr(message.chat, "title")
                    else "",
                    "permissions": {},
                    "updated_at": datetime.now(),
                    "admins": [],
                    "active": state_value,
                    "remove_messages": -1,
                    "admin_mode": False,
                }
                MongoDBClient.add_tgcalls_chats(document)
                current_client = config.fetchClient(message.chat.id)

            if current_client.get("active") is not True:
                logInfo(
                    f"chat not allowed to perform action : {message.chat.id} , {message.chat.type}"
                )

                msg, kbd = getMessage(message, "chat-not-allowed")
                return await client.send_message(
                    message.chat.id,
                    f"{msg}",
                    disable_web_page_preview=True,
                    reply_markup=kbd,
                )

            return await func(client, message, current_client)
        except Exception as ex:
            logException(f"Error in chat_allowed : {ex}", True)

    return decorator


def admin_check(func: Callable) -> Callable:
    async def decorator(client: Client, message: Message, current_client=None):
        try:
            chat_id = message.chat.id
            admins = config.getAdminForChat(chat_id)
            if message.from_user is None or message.from_user.id in [
                a["chat_id"] for a in admins
            ]:
                current_client = config.fetchClient(message.chat.id)
                current_client["is_admin"] = True
                return await func(client, message, current_client)
            else:
                logWarning(
                    f"Action blocked as user is not admin : {message.from_user} in chat {chat_id}, current_chat admins : {admins}"
                )
                m = await client.send_message(
                    message.chat.id,
                    f"**__This action can be performed only by admins.__**",
                )
                await delayDelete(m, 10)
        except Exception as ex:
            logException(f"Error in admin_check : {ex}", True)

    return decorator


def admin_mode_check(func: Callable) -> Callable:
    async def decorator(client: Client, message: Message, current_client):
        try:
            chat_id = message.chat.id
            if (
                current_client is not None
                and current_client.get("admin_mode") is not True
            ):
                current_client["is_admin"] = True
                return await func(client, message, current_client)
            admins = config.getAdminForChat(chat_id)
            if message.from_user is None or message.from_user.id in [
                a["chat_id"] for a in admins
            ]:
                current_client["is_admin"] = True
                return await func(client, message, current_client)

            logWarning(
                f"Action blocked as user is not admin and admin_mode is on : {message.from_user} , current_chat admins : {admins}"
            )
            msg = f"**❌ Admin mode is on in chat and your are not an admin[ Bot Admin ].**"
            msg = (
                msg
                + f"\n\n__Ask the admin to add you as admin using /auth command or disable the admin mode.__"
            )
            m = await client.send_message(message.chat.id, f"{msg}")
            await delayDelete(m, 10)
        except Exception as ex:
            logException(f"Error in admin_mode_check : {ex}", True)

    return decorator


def database_check(func: Callable) -> Callable:
    async def decorator(client: Client, message: Message):
        try:
            if MongoDBClient.client is None:
                m = await client.send_message(
                    message.chat.id,
                    f"**__This action is allowed only if mongo database url is provided in env parameter.__**",
                )
                await delayDelete(m, 10)
            return await func(client, message)
        except Exception as ex:
            logException(f"Error in database_check : {ex}", True)

    return decorator
