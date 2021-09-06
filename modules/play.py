from pyrogram import Client, filters
import os
import re
import callmanager
from utils.SongInfoFetcher import videoSearch
from helpers.decorators import (
    chat_allowed,
    delayDelete,
    admin_mode_check,
    send_message,
    edit_sent_message,
    parsePlayCommand,
)
from utils.Helper import Helper
from utils.Logger import *
from utils.Config import Config
from helpers.fromatMessages import getMessage
from helpers.GenerateCover import generate_cover, generate_blank_cover
import uuid
from pyrogram.raw.functions.phone import EditGroupCallTitle
from pyrogram.raw.functions.channels import GetFullChannel

helper = Helper()


def convert_seconds(seconds):
    seconds = seconds % (24 * 3600)
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60
    return "%02d:%02d" % (minutes, seconds)


Config = Config()


@Client.on_message(
    filters.command(["play", "play@vcplayerbot"]) & ~filters.edited & ~filters.bot
)
@chat_allowed
@admin_mode_check
async def play(client, message, current_client):
    try:
        requested_by = (
            {
                "chat_id": message.from_user.id,
                "title": message.from_user.first_name
                if hasattr(message.from_user, "first_name")
                else (
                    message.from_user.username
                    if hasattr(message.from_user, "username")
                    else "User"
                ),
                "is_admin": current_client.get("is_admin", False),
            }
            if message.from_user is not None
            else {
                "chat_id": message.chat.id,
                "title": message.chat.title
                if hasattr(message.chat, "title")
                else "Chat",
                "is_admin": current_client.get("is_admin", False),
            }
        )
        chat_id = message.chat.id
        logInfo(
            f"Playing command in chat : {chat_id} , requested_by : {requested_by}, command : {message.text}"
        )
        # check if song url or name is provided or not
        parsed_command = parsePlayCommand(
            message.text, current_client.get("is_admin", False)
        )
        logInfo(f"Parsed Command : {parsed_command}")
        if parsed_command["is_silent"] is True:
            await delayDelete(message)

        if helper.isEmpty(parsed_command["song_name"]):
            m = await send_message(
                client,
                message.chat.id,
                f"**Please provide a song url/name.\nLike :__/play faded by alan walker __**",
                parsed_command["is_silent"],
            )
            if (
                m is not None
                and current_client.get("remove_messages") is not None
                and current_client.get("remove_messages") > 0
            ):
                await delayDelete(m, current_client.get("remove_messages"))
            return

        music_player_instance = callmanager.MusicPlayer()
        pytgcalls_instance, err_message = music_player_instance.createGroupCallInstance(
            chat_id, current_client, client
        )
        if pytgcalls_instance is None:
            m = await send_message(
                client, message.chat.id, f"{err_message}", parsed_command["is_silent"]
            )
            if (
                m is not None
                and current_client.get("remove_messages") is not None
                and current_client.get("remove_messages") > 0
            ):
                await delayDelete(m, current_client.get("remove_messages"))
            return

        sent_msg = await send_message(
            client,
            message.chat.id,
            f"**__👀 Fetching song details... __**",
            parsed_command["is_silent"],
        )
        if parsed_command["is_youtube"] is True:
            songDetails = await videoSearch(
                parsed_command["song_name"],
                parsed_command["song_url"],
                parsed_command["is_video"],
                parsed_command["resolution"],
            )
        else:
            if parsed_command["song_url"] is None:
                m = await send_message(
                    client,
                    message.chat.id,
                    f"**__Please provide a direct streamable url.__",
                    parsed_command["is_silent"],
                )
                if (
                    m is not None
                    and current_client.get("remove_messages") is not None
                    and current_client.get("remove_messages") > 0
                ):
                    await delayDelete(m, current_client.get("remove_messages"))
                return
            songDetails = [
                {
                    "id": uuid.uuid4(),
                    "thumbnails": None,
                    "title": "Streaming URL",
                    "long_desc": "A SkTechHub Product",
                    "channel": "SkTechHub",
                    "duration": None,
                    "views": None,
                    "link": parsed_command["song_url"],
                    "resolution": "Default",
                    "is_video": True,
                }
            ]

        if songDetails is not None and len(songDetails) > 0:
            song_info = songDetails[0]
            song_info["is_repeat"] = parsed_command["is_repeat"]

            cover_file_name = None
            # generate thumbnail only if the song is first one and not for queue
            sent_msg = await edit_sent_message(
                sent_msg,
                f"**__ 🎥 Generating Thumbnail __**",
                parsed_command["is_silent"],
            )
            cover_file_name = None
            if parsed_command["is_silent"] is False:
                if (
                    song_info.get("thumbnails") is not None
                    and len(song_info["thumbnails"]) > 0
                ):
                    cover_file_name = f"images/{uuid.uuid4()}.png"
                    cover_file_name = await generate_cover(
                        song_info["title"],
                        song_info["thumbnails"][-1],
                        cover_file_name,
                    )
                else:
                    cover_file_name = f"images/{uuid.uuid4()}.png"
                    cover_file_name = await generate_blank_cover(cover_file_name)

            footer = None
            if Config.get("PLAYBACK_FOOTER") not in ["", None]:
                footer = f"{Config.get('PLAYBACK_FOOTER')}".replace("\\n", "\n")
            footer_val = (
                footer
                if footer is not None
                else "For any issues contact @voicechatsupport"
            )

            response = await pytgcalls_instance.start_playback(
                song_info, requested_by=requested_by
            )
            if response is not True:
                m = await edit_sent_message(
                    sent_msg,
                    f"**__😢 Unable to perform the required operation.__**\n{response}",
                    parsed_command["is_silent"],
                )
                if (
                    m is not None
                    and current_client.get("remove_messages") is not None
                    and current_client.get("remove_messages") > 0
                ):
                    await delayDelete(m, current_client.get("remove_messages"))
                return

            req_by = (
                f"[{requested_by['title']}](tg://user?id={requested_by['chat_id']})"
            )
            # edit group call title
            try:
                input_peer = await callmanager.user_app.resolve_peer(message.chat.id)
                chat = await callmanager.user_app.send(
                    GetFullChannel(channel=input_peer)
                )
                title_change = EditGroupCallTitle(
                    call=chat.full_chat.call, title="VC Player | By SkTechHub"
                )
                await callmanager.user_app.send(title_change)
            except Exception as ex:
                logWarning(f"Unable to change group call title : {ex}")

            if cover_file_name is not None and os.path.exists(cover_file_name):
                logInfo(f"Sending cover mesage in chat : {chat_id} : {cover_file_name}")

                caption = f"**{'📹' if song_info['is_video'] is True else '🎧'} Name:** `{(song_info['title'].strip())[:20]}`\n**⏱ Duration:** `{song_info['duration']}` | **📺 Res:** `{song_info['resolution']}`\n**💡 Requester:** {req_by}\n\n{footer_val}"
                m = await client.send_photo(
                    message.chat.id,
                    photo=cover_file_name,
                    caption=caption,
                )
                await sent_msg.delete()
                if cover_file_name is not None and os.path.exists(cover_file_name):
                    os.remove(cover_file_name)
                return
            else:
                m = await edit_sent_message(
                    sent_msg,
                    f"**✅ Playing Now **\n\n**🎧 Name:** `{(song_info['title'].strip())[:20]}`\n**⏱ Duration:** `{song_info['duration']}`\n**💡 Requester:** {req_by}\n\n{footer_val}",
                    parsed_command["is_silent"],
                )
                return

        m = await edit_sent_message(
            sent_msg,
            f"**__😢 Unable to find the required song, Please try again.__**",
            parsed_command["is_silent"],
        )
        if (
            m is not None
            and current_client.get("remove_messages") is not None
            and current_client.get("remove_messages") > 0
        ):
            await delayDelete(m, current_client.get("remove_messages"))
        return

    except Exception as ex:
        logException(f"Error in play: {ex}", True)
