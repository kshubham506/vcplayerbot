import asyncio
from pyrogram.types import Message, Chat
from utils.Logger import logException, logWarning
from cache import AsyncTTL
from utils import logger, config, helperClient, logInfo
import re
from pyrogram import Client


def hasRequiredPermission(user):
    try:
        required = [
            "can_post_messages",
            "can_invite_users",
            "can_manage_voice_chats",
            "can_promote_members",
        ]
        not_present = []
        for _ in required:
            if hasattr(user, _) is not True or user[_] is False:
                not_present.append(_)
        return len(not_present) == 0
    except Exception as ex:
        logException(f"Error in hasRequiredPermission : {ex}")


async def validate_session_string(api_id, api_hash, session_string, getUser=False):
    try:
        logInfo(f"Starting to validate user: {api_id}, {api_hash}")
        user_app = Client(
            session_string,
            api_id=int(api_id),
            api_hash=api_hash,
        )
        await user_app.start()
        me = await user_app.get_me()
        logInfo(f"validated session string: {me.id}")
        if getUser is False:
            await user_app.stop()
            return True, "", None, me.id, me.username
        else:
            return True, "", user_app, me.id, me.username
    except Exception as ex:
        logException(f"Error in validate_session_string : {ex}")
        return False, str(ex), None, "", ""


@AsyncTTL(time_to_live=20, maxsize=1024)
async def get_chat_member(client: Client, chat_id, bot_id):
    try:
        return await client.get_chat_member(chat_id, bot_id)
    except Exception as ex:
        logWarning(f"Error in get_chat_member : {ex} → {chat_id, bot_id}")


@AsyncTTL(time_to_live=60, maxsize=1024)
async def get_chat_details(client: Client, chat_id):
    try:
        chat_details: Chat = await client.get_chat(chat_id)
        return chat_details
    except Exception as ex:
        logException(f"Error in get_chat_details : {ex}")


@AsyncTTL(time_to_live=60, maxsize=1024)
async def get_chat_member_count(client: Client, chat_id):
    try:
        chat: Chat = await get_chat_details(client, chat_id)
        return chat.members_count
        # await client.get_chat_members_count(chat_id)
    except Exception as ex:
        logException(f"Error in get_chat_member_count : {ex}")


@AsyncTTL(time_to_live=60, maxsize=1024)
async def get_chat_member_list(client: Client, chat_id):
    try:
        await client.get_chat_members(client, chat_id)
    except Exception as ex:
        logException(f"Error in get_chat_member_list : {ex}")


@AsyncTTL(time_to_live=30, maxsize=1024)
async def getAlladmins(client: Client, chat_id):
    try:
        admins = await client.get_chat_members(chat_id, filter="administrators")
        admins = list(
            filter(
                lambda a: a.user is not None
                and (a.user.id == config.get("BOT_ID") or a.user.is_bot is False),
                admins,
            )
        )
        admins = [
            {
                "chat_id": i.user.id,
                "username": i.user.username if hasattr(i.user, "username") else "",
                "haspermission": hasRequiredPermission(i),
            }
            for i in admins
        ]
        return admins
    except Exception as ex:
        logException(f"Error while fetching admins : {ex}")
        return []


async def delayDelete(message, delay=1):
    try:
        if message is None:
            return
        else:
            await asyncio.sleep(delay)
            await message.delete()
    except Exception as ex:
        logException(f"Error in delayDelete : {ex}")


async def delete_message(message: Message):
    try:
        if message is not None and isinstance(message, Message):
            await message.delete()
    except Exception as ex:
        logException(f"Error in delete_message : {ex}")


async def send_message(client: Client, chat_id, message, reply_markup=None):
    try:
        if reply_markup is not None:
            return await client.send_message(
                chat_id,
                message,
                disable_web_page_preview=True,
                reply_markup=reply_markup,
            )
        return await client.send_message(
            chat_id,
            message,
            disable_web_page_preview=True,
        )
    except Exception as ex:
        logException(f"Error in send_message : {ex}")


async def send_photo(client: Client, chat_id, photo, caption, reply_markup=None):
    try:
        if reply_markup is not None:
            return await client.send_photo(
                chat_id, photo=photo, caption=caption, reply_markup=reply_markup
            )
        return await client.send_photo(chat_id, photo=photo, caption=caption)
    except Exception as ex:
        logException(f"Error in send_photo : {ex}")


async def edit_message(sent_message: Message, message):
    try:
        return await sent_message.edit(message, disable_web_page_preview=True)
    except Exception as ex:
        logException(f"Error in edit_message : {ex}")


def parseIncomingCommand(command, max_video_res=None, max_audio_res=None):
    try:
        is_video = helperClient.checkForArguments(command, "IS_VIDEO")
        resolution = helperClient.checkForArguments(command, "RES")
        if resolution is None:
            resolution = 256 if is_video is False else 480
        song_name = helperClient.checkForArguments(command, "NAME")
        is_repeat = helperClient.checkForArguments(command, "REPEAT")
        only_audio = helperClient.checkForArguments(command, "ONLY_AUDIO")
        lip_sync = helperClient.checkForArguments(command, "LIP_SYNC")
        _urls = helperClient.getUrls(song_name)
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
        switched = False
        if is_video is False and max_audio_res and int(resolution) > max_audio_res:
            resolution = max_audio_res
            switched = True
        elif is_video is True and max_video_res and int(resolution) > max_video_res:
            resolution = max_video_res
            switched = True

        return {
            "is_video": is_video,
            "resolution": resolution,
            "is_youtube": is_youtube,
            "resolution_switched": switched,
            "is_url": is_url,
            "song_url": song_url,
            "song_name": song_name,
            "is_repeat": is_repeat is True,
            "only_audio": only_audio is True,
            "lip_sync": lip_sync is True,
        }
    except Exception as ex:
        logException(f"Error in parseIncomingCommand : {ex}")
