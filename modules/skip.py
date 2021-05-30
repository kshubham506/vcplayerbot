from pyrogram import Client, filters


import callmanager
from helpers.decorators import chat_allowed, delayDelete, admin_mode_check
from utils.Logger import *
from helpers.fromatMessages import getMessage


@Client.on_message(filters.command(['skip', 'skip@vcplayerbot']) & ~filters.edited & ~filters.bot)
@chat_allowed
@admin_mode_check
async def skip(client, message, current_client):
    try:
        chat_id = message.chat.id
        logInfo(f"Skip command in chat : {chat_id}")

        music_player_instance = callmanager.MusicPlayer()
        pytgcalls_instance, err_message = music_player_instance.createGroupCallInstance(
            chat_id, current_client, client)
        if pytgcalls_instance is None:
            m = await client.send_message(message.chat.id, f"{err_message}")
            if current_client.get('remove_messages') is not None and current_client.get('remove_messages') > 0:
                await delayDelete(m, current_client.get('remove_messages'))
            return

        if pytgcalls_instance.active is not True:
            msg, kbd = getMessage(message, 'start-voice-chat')
            m = await client.send_message(message.chat.id, f"{msg}", disable_web_page_preview=True, reply_markup=kbd)
            if current_client.get('remove_messages') is not None and current_client.get('remove_messages') > 0:
                await delayDelete(m, current_client.get('remove_messages'))
            return

        status, resp_message = await pytgcalls_instance.skipPlayBack(fromCommand=True)
        if status is True:
            pytgcalls_instance.status = "playing"
            pytgcalls_instance.active = True
        m = await client.send_message(message.chat.id, f"{resp_message}")
        if current_client.get('remove_messages') is not None and current_client.get('remove_messages') > 0:
            await delayDelete(m, current_client.get('remove_messages'))
        return

    except Exception as ex:
        logException(f"Error in skip: {ex}", True)
