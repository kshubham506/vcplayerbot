from decorators.validate_command_pre_check import validate_command_pre_check
from decorators.save_user_chat_db import save_user_chat_in_db
from decorators.is_bot_admin import is_bot_admin
from pyrogram import Client, filters
from utils import logInfo, logException, logWarning, helperClient
from extras.callmanager import MusicPlayer


@Client.on_message(
    filters.command(["play", "play@vcplayerbot"])
    & ~filters.edited
    & ~filters.bot
    & ~filters.private
)
@save_user_chat_in_db
@is_bot_admin
@validate_command_pre_check
async def play(client: Client, message, current_client):
    try:
        current_chat = message.chat

        logInfo(
            f"Playing command in chat : {current_chat.id} , requested_by : {current_client['requested_by']}"
        )
        # check if song url or name is provided or not
        parsed_command = current_client["parsed_command"]

        if helperClient.isEmpty(parsed_command["song_name"]):
            await client.send_message(
                current_chat.id,
                f"__Please provide a media url or name.\nFor instance → **/play summer of 69**__",
            )

        # music_player_instance = callmanager.MusicPlayer()
        # (
        #     pytgcalls_instance,
        #     err_message,
        # ) = await music_player_instance.createGroupCallInstance(
        #     chat_id, current_client, client
        # )
        # if pytgcalls_instance is None:
        #     m = await send_message(
        #         client, message.chat.id, f"{err_message}", parsed_command["is_silent"]
        #     )
        #     if (
        #         m is not None
        #         and current_client.get("remove_messages") is not None
        #         and current_client.get("remove_messages") > 0
        #     ):
        #         await delayDelete(m, current_client.get("remove_messages"))
        #     return

        # sent_msg = await send_message(
        #     client,
        #     message.chat.id,
        #     f"**__👀 Fetching {'video' if parsed_command['is_video'] is True else 'audio'} details... __**",
        #     parsed_command["is_silent"],
        # )
        # if parsed_command["is_youtube"] is True:
        #     songDetails = await videoSearch(
        #         parsed_command["song_name"],
        #         parsed_command["song_url"],
        #         parsed_command["is_video"],
        #         parsed_command["resolution"],
        #     )
        # else:
        #     if parsed_command["song_url"] is None:
        #         m = await send_message(
        #             client,
        #             message.chat.id,
        #             f"**__Please provide a direct streamable url.__",
        #             parsed_command["is_silent"],
        #         )
        #         if (
        #             m is not None
        #             and current_client.get("remove_messages") is not None
        #             and current_client.get("remove_messages") > 0
        #         ):
        #             await delayDelete(m, current_client.get("remove_messages"))
        #         return
        #     songDetails = [
        #         {
        #             "id": uuid.uuid4(),
        #             "thumbnails": None,
        #             "title": "Streaming URL",
        #             "long_desc": "A SkTechHub Product",
        #             "channel": "SkTechHub",
        #             "duration": None,
        #             "views": None,
        #             "link": parsed_command["song_url"],
        #             "audio_link": None,
        #             "resolution": "Default",
        #             "is_video": True,
        #         }
        #     ]

        # if songDetails is not None and len(songDetails) > 0:
        #     song_info = songDetails[0]
        #     song_info["is_repeat"] = parsed_command["is_repeat"]
        #     song_info["only_audio"] = parsed_command["only_audio"]
        #     song_info["lip_sync"] = parsed_command["lip_sync"]

        #     cover_file_name = None
        #     # generate thumbnail only if the song is first one and not for queue
        #     sent_msg = await edit_sent_message(
        #         sent_msg,
        #         f"**__ 🎥 Generating Thumbnail __**",
        #         parsed_command["is_silent"],
        #     )
        #     cover_file_name = None
        #     if parsed_command["is_silent"] is False:
        #         if (
        #             song_info.get("thumbnails") is not None
        #             and len(song_info["thumbnails"]) > 0
        #         ):
        #             cover_file_name = f"images/{uuid.uuid4()}.png"
        #             cover_file_name = await generate_cover(
        #                 song_info["title"],
        #                 song_info["thumbnails"][-1],
        #                 cover_file_name,
        #             )
        #         else:
        #             cover_file_name = f"images/{uuid.uuid4()}.png"
        #             cover_file_name = await generate_blank_cover(cover_file_name)

        #     footer = None
        #     if Config.get("PLAYBACK_FOOTER") not in ["", None]:
        #         footer = f"{Config.get('PLAYBACK_FOOTER')}".replace("\\n", "\n")
        #     footer_val = (
        #         footer if footer is not None else "For any issues contact @voicechatsupport"
        #     )

        #     response = await pytgcalls_instance.start_playback(
        #         song_info, requested_by=requested_by
        #     )
        #     if response is not True:
        #         m = await edit_sent_message(
        #             sent_msg,
        #             f"**__😢 Unable to perform the required operation.__**\n{response}",
        #             parsed_command["is_silent"],
        #         )
        #         if (
        #             m is not None
        #             and current_client.get("remove_messages") is not None
        #             and current_client.get("remove_messages") > 0
        #         ):
        #             await delayDelete(m, current_client.get("remove_messages"))
        #         return

        #     req_by = f"[{requested_by['title']}](tg://user?id={requested_by['chat_id']})"

        #     if cover_file_name is not None and os.path.exists(cover_file_name):
        #         logInfo(f"Sending cover mesage in chat : {chat_id} : {cover_file_name}")

        #         caption = f"**{'📹' if song_info['is_video'] is True else '🎧'} Name:** `{(song_info['title'].strip())[:20]}`\n**⏱ Duration:** `{song_info['duration']}` | **📺 Res:** `{song_info['resolution']}`\n**💡 Requester:** {req_by}\n\n{footer_val}"
        #         m = await client.send_photo(
        #             message.chat.id,
        #             photo=cover_file_name,
        #             caption=caption,
        #         )
        #         await sent_msg.delete()
        #         if cover_file_name is not None and os.path.exists(cover_file_name):
        #             os.remove(cover_file_name)
        #         return
        #     else:
        #         m = await edit_sent_message(
        #             sent_msg,
        #             f"**✅ Playing Now **\n\n**🎧 Name:** `{(song_info['title'].strip())[:20]}`\n**⏱ Duration:** `{song_info['duration']}`\n**💡 Requester:** {req_by}\n\n{footer_val}",
        #             parsed_command["is_silent"],
        #         )
        #         return

        # m = await edit_sent_message(
        #     sent_msg,
        #     f"**__😢 Unable to find the required song, Please try again.__**",
        #     parsed_command["is_silent"],
        # )
        # if (
        #     m is not None
        #     and current_client.get("remove_messages") is not None
        #     and current_client.get("remove_messages") > 0
        # ):
        #     await delayDelete(m, current_client.get("remove_messages"))
        # return
    except Exception as ex:
        logException(f"Error in play command : {ex}")
