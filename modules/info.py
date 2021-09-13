from decorators.extras import send_message
from decorators.save_user_chat_db import save_user_chat_in_db
from decorators.message_factory import getMessage
from pyrogram import Client, filters

from utils import logException


@Client.on_message(
    filters.command(["help", "help@vcplayerbot"]) & ~filters.edited & ~filters.bot
)
@save_user_chat_in_db
async def info(client, message, current_client):
    try:
        if current_client.get("is_private") is True:
            msg, kbd = getMessage(message, "help-private-message")
        else:
            msg, kbd = getMessage(message, "help-group-message")
        return await client.send_message(
            message.chat.id, f"{msg}", disable_web_page_preview=True, reply_markup=kbd
        )
    except Exception as ex:
        await send_message(client, message.chat.id, f"__Error : {ex}__")
        logException(f"Error in info: {ex}", True)


@Client.on_message(filters.command(["start", "start@vcplayerbot"]) & ~filters.edited)
@save_user_chat_in_db
async def startCommand(client, message, current_client):
    try:
        if current_client.get("is_private") is True:
            msg, kbd = getMessage(message, "start-private-message")
        else:
            msg, kbd = getMessage(message, "start-group-message")
        return await client.send_message(
            message.chat.id, f"{msg}", disable_web_page_preview=True, reply_markup=kbd
        )
    except Exception as ex:
        await send_message(client, message.chat.id, f"__Error : {ex}__")
        logException(f"Error in startCommand: {ex}", True)
