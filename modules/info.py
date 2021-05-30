from pyrogram import Client, filters


import callmanager
from helpers.decorators import chat_allowed, admin_check, delayDelete
from helpers.fromatMessages import getMessage
from utils.Logger import *
from utils.Config import Config

Config = Config()


@Client.on_message(filters.command(['info', 'info@vcplayerbot']) & ~filters.edited & ~filters.bot)
@chat_allowed
@admin_check
async def info(client, message, current_client):
    try:
        chat_id = message.chat.id
        logInfo(f"Info command in chat : {chat_id}")

        forceCreate = False
        if message.from_user is not None and hasattr(message.from_user, 'id') and message.from_user.id in [i['chat_id'] for i in Config.get('GLOBAL_ADMINS')]:
            forceCreate = True

        music_player_instance = callmanager.MusicPlayer()
        pytgcalls_instance, err_message = music_player_instance.createGroupCallInstance(
            chat_id, current_client, client, forceCreate)
        if pytgcalls_instance is None:
            return await client.send_message(message.chat.id, f"{err_message}")

        status, resp_message = await pytgcalls_instance.getCurrentInfo(message.from_user.id if message.from_user is not None and hasattr(message.from_user, 'id') else -1)

        m = await client.send_message(message.chat.id, f"{resp_message}")
        if current_client.get('remove_messages') is not None and current_client.get('remove_messages') > 0:
            await delayDelete(m, current_client.get('remove_messages'))
        return

    except Exception as ex:
        logException(f"Error in info: {ex}", True)


@Client.on_message(filters.command(['start', 'start@vcplayerbot', 'help', 'help@vcplayerbot']) & ~filters.edited)
async def help(client, message, current_client=None):
    try:
        chat_id = message.chat.id
        logInfo(f"help command in chat : {chat_id}")

        msg, kbd = getMessage(message, 'help-msg')

        return await client.send_message(message.chat.id, f"{msg}", disable_web_page_preview=True, reply_markup=kbd)

    except Exception as ex:
        logException(f"Error in help: {ex}", True)
