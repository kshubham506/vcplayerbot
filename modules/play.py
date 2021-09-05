from pyrogram import Client, filters
import os
import re
import callmanager
from utils.SongInfoFetcher import videoSearch
from helpers.decorators import chat_allowed, delayDelete, admin_mode_check
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


def parsePlayCommand(command):
    is_video = helper.checkForArguments(command, "IS_VIDEO")
    resolution = helper.checkForArguments(command, "RES")
    if resolution is None:
        resolution = 256 if is_video is False else 480
    song_name = helper.checkForArguments(command, "NAME")
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
    }


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
            }
            if message.from_user is not None
            else {
                "chat_id": message.chat.id,
                "title": message.chat.title
                if hasattr(message.chat, "ttile")
                else "Chat",
            }
        )
        chat_id = message.chat.id
        logInfo(f"Playing command in chat : {chat_id} , requested_by : {requested_by}")
        # check if song url or name is provided or not
        parsed_command = parsePlayCommand(message.text)

        if helper.isEmpty(parsed_command["song_name"]):
            m = await client.send_message(
                message.chat.id,
                f"**Please provide a song url/name.\nLike :__/play faded by alan walker __**",
            )
            if (
                current_client.get("remove_messages") is not None
                and current_client.get("remove_messages") > 0
            ):
                await delayDelete(m, current_client.get("remove_messages"))
            return

        music_player_instance = callmanager.MusicPlayer()
        pytgcalls_instance, err_message = music_player_instance.createGroupCallInstance(
            chat_id, current_client, client
        )
        if pytgcalls_instance is None:
            m = await client.send_message(message.chat.id, f"{err_message}")
            if (
                current_client.get("remove_messages") is not None
                and current_client.get("remove_messages") > 0
            ):
                await delayDelete(m, current_client.get("remove_messages"))
            return

        sent_msg = await client.send_message(
            message.chat.id, f"**__👀 Fetching song details... __**"
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
                m = await client.send_message(
                    message.chat.id, f"**__Please provide a direct streamable url.__"
                )
                if (
                    current_client.get("remove_messages") is not None
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
                    "resolution": 480,
                    "is_video": True,
                }
            ]

        if songDetails is not None and len(songDetails) > 0:
            song_info = songDetails[0]

            cover_file_name = None
            # generate thumbnail only if the song is first one and not for queue
            sent_msg = await sent_msg.edit(f"**__ 🎥 Generating Thumbnail __**")
            cover_file_name = None
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
                ("\n" + footer)
                if footer is not None
                else "\nFor any issues contact @voicechatsupport"
            )
            print("Start playback")
            response = await pytgcalls_instance.start_playback(
                song_info, requested_by=requested_by
            )
            if response is not True:
                m = await sent_msg.edit(
                    f"**__😢 Unable to perform the required operation.__**\n{response}"
                )
                if (
                    current_client.get("remove_messages") is not None
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

                caption = f"**{'📹' if song_info['is_video'] is True else '🎧'} Name:** `{(song_info['title'].strip())[:20]}`\n**⏱ Duration:** `{song_info['duration']} sec`\n**💡 Requester:** {req_by}\n\n`Join voice chat to listen to the song.`{footer_val}"
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
                m = await sent_msg.edit(
                    f"**✅ Playing Now **\n\n**🎧 Name:** `{(song_info['title'].strip())[:20]}`\n**⏱ Duration:** `{song_info['duration']}`\n**💡 Requester:** {req_by}{footer_val}"
                )
                return

        m = await sent_msg.edit(
            f"**__😢 Unable to find the required song, Please try again.__**"
        )
        if (
            current_client.get("remove_messages") is not None
            and current_client.get("remove_messages") > 0
        ):
            await delayDelete(m, current_client.get("remove_messages"))
        return

    except Exception as ex:
        logException(f"Error in play: {ex}", True)
