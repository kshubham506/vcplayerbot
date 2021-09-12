from pyrogram import Client, filters
from decorators.validate_command_pre_check import validate_command_pre_check
from decorators.save_user_chat_db import save_user_chat_in_db
from decorators.is_bot_admin import is_bot_admin
from decorators.extras import send_message, edit_message
from utils import logException, logInfo, logWarning
from extras import music_player


@Client.on_message(
    filters.command(["pause", "pause@vcplayerbot"])
    & ~filters.edited
    & ~filters.bot
    & ~filters.private
)
@save_user_chat_in_db
@is_bot_admin
@validate_command_pre_check
async def pause(client, message, current_client):
    try:
        current_chat = message.chat
        logInfo(f"Pause command in chat : {current_chat.id}")
        (
            gc_instance,
            err_message,
        ) = await music_player.getGroupCallInstance(current_chat.id)
        if gc_instance is None:
            await send_message(client, current_chat.id, f"{err_message}")
            return
        await gc_instance.set_pause_playback(pause=True)
    except Exception as ex:
        await send_message(client, message.chat.id, f"__Error while pausing : {ex}__")
        logException(f"Error in pause: {ex}", True)


@Client.on_message(
    filters.command(["resume", "resume@vcplayerbot"])
    & ~filters.edited
    & ~filters.bot
    & ~filters.private
)
@save_user_chat_in_db
@is_bot_admin
@validate_command_pre_check
async def resume(client, message, current_client):
    try:
        current_chat = message.chat
        logInfo(f"resume command in chat : {current_chat.id}")
        (
            gc_instance,
            err_message,
        ) = await music_player.getGroupCallInstance(current_chat.id)
        if gc_instance is None:
            await send_message(client, current_chat.id, f"{err_message}")
            return
        await gc_instance.set_pause_playback(pause=False)
    except Exception as ex:
        await send_message(client, message.chat.id, f"__Error while resuming : {ex}__")
        logException(f"Error in resume: {ex}", True)
