from pyrogram import Client, filters
from decorators.extras import send_message, edit_message, send_photo
from utils import logException, logInfo, logWarning, config
import asyncio
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

"""
Only allowed by sudo user
"""


@Client.on_message(
    filters.command(["promote", "promote@vcplayerbot"])
    & ~filters.edited
    & ~filters.bot
    & filters.private
)
async def promote(client, message):
    try:
        if message.from_user.id in config.get("SUDO_USER"):
            is_message_confirmed = (
                len(message.command) > 2 and message.command[2] == "confirm"
            )
            chat_ids = [c.strip() for c in message.command[1].split(",")]
            if not chat_ids:
                return await send_message(
                    client,
                    message.from_user.id,
                    "__Please provide chats ids as second argument separated by comama.__",
                )
            promotional_data = config.get("PROMOTIONAL_DATA")
            if not promotional_data:
                return await send_message(
                    client,
                    message.from_user.id,
                    "__Please add the promotional message in database as **PROMOTIONAL_MSG**.__",
                )
            if not is_message_confirmed:
                await send_message(
                    client,
                    message.from_user.id,
                    f"__Confirm the below message to **{len(chat_ids)} users** .__",
                )
                chat_ids = config.get("SUDO_USER")
            else:
                await send_message(
                    client,
                    message.from_user.id,
                    f"__Started to send message to **{len(chat_ids)} users** .__",
                )
            logInfo(f"Starting to send message to {len(chat_ids)} users.")
            promotional_msg = promotional_data.get("message").replace("\\n", "\n")
            if promotional_data.get("button_text") is not None:
                keyboard = InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                promotional_data.get("button_text"),
                                url=promotional_data.get("button_url"),
                            ),
                        ]
                    ]
                )
            else:
                keyboard = None
            for count, chat in enumerate(chat_ids):
                logInfo(
                    f"{count} → Sending to chat: {chat}, Left: {len(chat_ids)-count-1}"
                )
                if promotional_data.get("image"):
                    await send_photo(
                        client,
                        chat,
                        promotional_data.get("image"),
                        promotional_msg,
                        reply_markup=keyboard,
                    )
                else:
                    await send_message(
                        client, chat, promotional_msg, reply_markup=keyboard
                    )
                await asyncio.sleep(5)

            await send_message(
                client,
                message.from_user.id,
                f"__Sending promotional message ended **{len(chat_ids)} users** .__",
            )
    except Exception as ex:
        await send_message(client, message.chat.id, f"__Error while promoting : {ex}__")
        logException(f"Error in promote: {ex}", True)
