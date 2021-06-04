from pyrogram import Client, filters


import callmanager
from helpers.decorators import chat_allowed, delayDelete, admin_mode_check
from utils.Logger import *


@Client.on_message(filters.command(['stop', 'stop@vcplayerbot']) & ~filters.edited & ~filters.bot)
@chat_allowed
@admin_mode_check
async def stop(client, message, current_client):
    try:
        chat_id = message.chat.id
        logInfo(f"Stop command in chat : {chat_id}")

        music_player_instance = callmanager.MusicPlayer()
        pytgcalls_instance, err_message = music_player_instance.createGroupCallInstance(
            chat_id, current_client, client)
        if pytgcalls_instance is None:
            m = await client.send_message(message.chat.id, f"{err_message}")
            if current_client.get('remove_messages') is not None and current_client.get('remove_messages') > 0:
                await delayDelete(m, current_client.get('remove_messages'))
            return

        force_stop = False
        if len(message.command) > 1 and message.command[1] == "force":
            force_stop = True
        if force_stop is False and pytgcalls_instance.active is not True:
            m = await client.send_message(message.chat.id, f"**🙅‍♂️ No song is being played which can be stopped, start one by sending `/play song_name/url.`**")
            if current_client.get('remove_messages') is not None and current_client.get('remove_messages') > 0:
                await delayDelete(m, current_client.get('remove_messages'))
            return

        status, resp_message = await pytgcalls_instance.stopPlayBack(False, False, force_stop)

        m = await client.send_message(message.chat.id, f"{resp_message}")
        if current_client.get('remove_messages') is not None and current_client.get('remove_messages') > 0:
            await delayDelete(m, current_client.get('remove_messages'))
        return

    except Exception as ex:
        logException(f"Error in stop: {ex}", True)
