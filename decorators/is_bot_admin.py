from typing import Callable
from pyrogram import Client
from pyrogram.filters import private_filter
from pyrogram.types import Message, CallbackQuery

from utils import logException, logInfo, config, logger
from decorators.extras import get_chat_member


def is_bot_admin(func: Callable) -> Callable:
    async def decorator(client: Client, incomingPayload, current_client):
        try:
            if isinstance(incomingPayload, CallbackQuery) is True:
                message: Message = incomingPayload.message
            else:
                message: Message = incomingPayload

            current_chat = message.chat
            if await private_filter(None, None, message) is not True:
                missing_permissions = []
                if current_chat.permissions:
                    required_permissions = [
                        "can_send_messages",
                        "can_send_media_messages",
                    ]
                    missing_permissions = list(
                        filter(
                            lambda perm: hasattr(current_chat.permissions, perm) is True
                            and getattr(current_chat.permissions, perm) is not True,
                            required_permissions,
                        )
                    )
                if not missing_permissions:
                    botInfo = await get_chat_member(
                        client, current_chat.id, config.get("BOT_ID")
                    )
                    required_permissions = [
                        "can_delete_messages",
                        "can_manage_voice_chats",
                        "can_promote_members",
                        "can_invite_users",
                    ]
                    missing_permissions = list(
                        filter(
                            lambda perm: botInfo is None
                            or hasattr(botInfo, perm) is False
                            or getattr(botInfo, perm) is not True,
                            required_permissions,
                        )
                    )
                if missing_permissions:
                    missing_permissions = "\n".join(missing_permissions)
                    msg = f"__Please add the bot **{config.get('BOT_USERNAME')}** as an admin or at least provide the below mandatory permissions to it__.\n__Wait for at least 10 sec after granting the permissions.__\n\n`{missing_permissions}`"
                    return await client.send_message(
                        message.chat.id, f"{msg}", disable_web_page_preview=True
                    )

            return await func(client, incomingPayload, current_client)
        except Exception as ex:
            logException(f"Error in is_bot_admin: {ex}")

    return decorator
