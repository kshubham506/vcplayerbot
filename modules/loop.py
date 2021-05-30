from pyrogram import Client, filters


import callmanager
from helpers.decorators import chat_allowed, delayDelete, admin_mode_check
from utils.Logger import *
from helpers.fromatMessages import getMessage
from utils.Config import Config

Config = Config()


@Client.on_message(filters.command(['loop', 'loop@vcplayerbot']) & ~filters.edited & ~filters.bot)
@chat_allowed
@admin_mode_check
async def loopPlay(client, message, current_client):
    try:
        chat_id = message.chat.id
        logInfo(f"loopPlay command in chat : {chat_id}")
        command = None
        found = False
        if len(message.command) > 1:
            global_user = False
            if message.from_user is not None and hasattr(message.from_user, 'id') and message.from_user.id in [i['chat_id'] for i in Config.get('GLOBAL_ADMINS')]:
                global_user = True
            if message.command[1].lower() in ['off']:
                command = "off"
                found = True
            else:
                try:
                    command = int(message.command[1])
                    if command > 1 and command <= 5 or global_user is True:
                        found = True
                except Exception as ex:
                    pass

        if found is False:
            msg = f"**❌ Invalid Command :**\n• `/loop off` - __Turn off loop for all songs.__\n• `/loop [2-5]` - __Loop songs [x] times , x must be between 2-5.__"
            m = await client.send_message(message.chat.id, f"{msg}")
            if current_client.get('remove_messages') is not None and current_client.get('remove_messages') > 0:
                await delayDelete(m, current_client.get('remove_messages'))
            return

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

        if command == "off":
            pytgcalls_instance.repeatCount = 1
            pytgcalls_instance.currentRepeatCount = 0
            m = await client.send_message(message.chat.id, f"✔️ **__Done loop playback turned off, now all songs will be played just once.__**")
        else:
            pytgcalls_instance.repeatCount = command
            m = await client.send_message(message.chat.id, f"✔️ **__Done Loop Playback turned on, now all songs will repeat {command} times.__**")

        if current_client.get('remove_messages') is not None and current_client.get('remove_messages') > 0:
            await delayDelete(m, current_client.get('remove_messages'))
        return

    except Exception as ex:
        logException(f"Error in loopPlay: {ex}", True)
