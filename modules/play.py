from pyrogram import Client, filters
import os
import asyncio
import callmanager
from utils.Downloader import Downloader
from utils.SongInfoFetcher import YouTubeSearch
from helpers.decorators import chat_allowed, delayDelete, admin_mode_check
from utils.Logger import *
from utils.Config import Config
from helpers.fromatMessages import getMessage
from helpers.GenerateCover import generate_cover
import uuid
from pyrogram.raw.functions.phone import EditGroupCallTitle
from pyrogram.raw.functions.channels import GetFullChannel


def convert_seconds(seconds):
    seconds = seconds % (24 * 3600)
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60
    return "%02d:%02d" % (minutes, seconds)


# Convert hh:mm:ss to seconds
def time_to_seconds(time):
    stringt = str(time)
    return sum(int(x) * 60 ** i for i, x in enumerate(reversed(stringt.split(":"))))


DownloaderService = Downloader()
Config = Config()


@Client.on_message(filters.command(['play', 'play@vcplayerbot']) & ~filters.edited & ~filters.bot)
@chat_allowed
@admin_mode_check
async def play(client, message, current_client):
    try:
        requested_by = {"chat_id": message.from_user.id, "title": message.from_user.first_name if hasattr(message.from_user, 'first_name') else (message.from_user.username if hasattr(
            message.from_user, 'username') else 'User')} if message.from_user is not None else {"chat_id": message.chat.id, "title": message.chat.title if hasattr(message.chat, 'ttile') else 'Chat'}
        chat_id = message.chat.id
        logInfo(
            f"Playing command in chat : {chat_id} , requested_by : {requested_by}")
        # check if song url or name is provided or not
        song_url_name = message.text.split(" ")
        if len(song_url_name) > 1:
            song_url_name = " ".join(song_url_name[1:])
        else:
            m = await client.send_message(message.chat.id, f"**Invalid Command, Please provide a song url/name.\nEg:__/play faded by alan walker __**")
            if current_client.get('remove_messages') is not None and current_client.get('remove_messages') > 0:
                await delayDelete(m, current_client.get('remove_messages'))
            return

        # check if the bot has permission

        music_player_instance = callmanager.MusicPlayer()
        pytgcalls_instance, err_message = music_player_instance.createGroupCallInstance(
            chat_id, current_client, client)
        if pytgcalls_instance is None:
            m = await client.send_message(message.chat.id, f"{err_message}")
            if current_client.get('remove_messages') is not None and current_client.get('remove_messages') > 0:
                await delayDelete(m, current_client.get('remove_messages'))
            return

        current_call = await pytgcalls_instance.getCurrentCall()
        if current_call is None:
            # if there are no active voice chats
            msg, kbd = getMessage(message, 'start-voice-chat')
            m = await client.send_message(message.chat.id, f"{msg}", disable_web_page_preview=True, reply_markup=kbd)
            if current_client.get('remove_messages') is not None and current_client.get('remove_messages') > 0:
                await delayDelete(m, current_client.get('remove_messages'))
            return

        # pre check if done only for new songs(first time playbacks)
        if pytgcalls_instance.active is not True:
            preCheck = await pytgcalls_instance.preCheck(client, callmanager.user_app)
            if preCheck is not True:
                m = await client.send_message(message.chat.id, f"{preCheck}")
                if current_client.get('remove_messages') is not None and current_client.get('remove_messages') > 0:
                    await delayDelete(m, current_client.get('remove_messages'))
                return

        sent_msg = await client.send_message(message.chat.id, f"**__Fetching song details... __**")
        songDetails = await YouTubeSearch(song_url_name, 1)

        if songDetails is not None and len(songDetails) > 0:
            song_info = songDetails[0]
            if time_to_seconds(song_info['duration']) > (int(Config.get('ALLOWED_SONG_DURATION_IN_MIN'))*60):
                m = await sent_msg.edit(f"**__😢 The specified song is too long, Please use a song with less than {Config.get('ALLOWED_SONG_DURATION_IN_MIN')} min duration.__**")
                if current_client.get('remove_messages') is not None and current_client.get('remove_messages') > 0:
                    await delayDelete(m, current_client.get('remove_messages'))
                return

            else:
                cover_file_name = None
                # generate thumbnail only if the song is first one and not for queue
                if pytgcalls_instance.active is not True:
                    sent_msg = await sent_msg.edit(f"**__ 🎥 Generating Thumbnail __**")
                    cover_file_name = None
                    if song_info.get('thumbnails') is not None and len(song_info['thumbnails']) > 0:
                        cover_file_name = f"images/{uuid.uuid4()}.png"
                        cover_file_name = await generate_cover(
                            song_info['title'], song_info['thumbnails'][-1], cover_file_name)

                # download and process the song
                sent_msg = await sent_msg.edit(f"**__ ⏱ Beep... Bop... Processing [May Take 30-40 sec]__**")
                filename = await DownloaderService.download_and_transcode_song(f"{song_info['link']}")
                if filename is None:
                    m = await sent_msg.edit(f"**__✖️ Critical Error while post procesing, Try again! __**")
                    if current_client.get('remove_messages') is not None and current_client.get('remove_messages') > 0:
                        await delayDelete(m, current_client.get('remove_messages'))
                    return
                else:
                    footer = None
                    if Config.get('PLAYBACK_FOOTER') not in ['', None]:
                        footer = f"{Config.get('PLAYBACK_FOOTER')}".replace(
                            '\\n', '\n')
                    footer_val = (
                        '\n'+footer) if footer is not None else '\nFor any issues contact @voicechatsupport'

                    # if curernt call is there , then add it to queue
                    if pytgcalls_instance.active is True:
                        status, resp_message = await pytgcalls_instance.addSongsInQueue(filename, song_info, requested_by)
                        m = await sent_msg.edit(f"{resp_message}")
                        if current_client.get('remove_messages') is not None and current_client.get('remove_messages') > 0:
                            await delayDelete(m, current_client.get('remove_messages'))

                        return

                    # direct play
                    await pytgcalls_instance.changeFile(
                        filename, song_info, requested_by)

                    response = await pytgcalls_instance.start_playback(filename, song_info, requested_by)
                    if response is not True:
                        m = await sent_msg.edit(f"**__😢 Unable to perform the required operation.__**\n{response}")
                        if current_client.get('remove_messages') is not None and current_client.get('remove_messages') > 0:
                            await delayDelete(m, current_client.get('remove_messages'))

                        return
                    else:

                        req_by = f"[{requested_by['title']}](tg://user?id={requested_by['chat_id']})"

                        # edit group call title
                        try:
                            input_peer = await callmanager.user_app.resolve_peer(message.chat.id)
                            chat = await callmanager.user_app.send(GetFullChannel(channel=input_peer))
                            title_change = EditGroupCallTitle(call=chat.full_chat.call,
                                                              title="Song Player | By SkTechHub")
                            await callmanager.user_app.send(title_change)
                        except Exception as ex:
                            logWarning(
                                f"Unable to change group call title : {ex}")

                        if cover_file_name is not None and os.path.exists(cover_file_name):
                            logInfo(
                                f"Sending cover mesage in chat : {chat_id} : {cover_file_name}")

                            caption = f"**🎧 Name:** `{(song_info['title'].strip())[:20]}`\n**⏱ Duration:** `{song_info['duration']}`\n**💡 Requester:** {req_by}\n\n`Join voice chat to listen to the song.`{footer_val}"
                            m = await client.send_photo(
                                message.chat.id,
                                photo=cover_file_name,
                                caption=caption,
                            )
                            await sent_msg.delete()
                            if cover_file_name is not None and os.path.exists(cover_file_name):
                                os.remove(cover_file_name)
                        else:

                            m = await sent_msg.edit(f"**✅ Playing Now **\n\n**🎧 Name:** `{(song_info['title'].strip())[:20]}`\n**⏱ Duration:** `{song_info['duration']}`\n**💡 Requester:** {req_by}{footer_val}")
                        # if current_client.get('remove_messages') is not None and current_client.get('remove_messages') > 0:
                        #     await delayDelete(m, current_client.get('remove_messages'))
                        return
                    return

        m = await sent_msg.edit(f"**__😢 Unable to find the required song, Please try again.__**")
        if current_client.get('remove_messages') is not None and current_client.get('remove_messages') > 0:
            await delayDelete(m, current_client.get('remove_messages'))
        return

    except Exception as ex:
        logException(f"Error in play: {ex}", True)
