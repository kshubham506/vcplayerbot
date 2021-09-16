from decorators.must_have_mongo import must_have_mongo
from decorators.extras import delayDelete
from utils.Logger import logWarning
from decorators.save_user_chat_db import save_user_chat_in_db
from decorators.is_bot_admin import is_bot_admin
from pyrogram import Client
from utils import mongoDBClient, config, loop, logException


@Client.on_callback_query()
@must_have_mongo
@save_user_chat_in_db
@is_bot_admin
async def answer(client, callback_query, current_client):
    try:
        if callback_query.data == "authorize-user-bot":
            if current_client.get("is_admin") is True:
                # create temp auth doc
                mongoDBClient.generate_auth_document(
                    current_client["from_chat"].id, current_client["from_user"].id
                )
                try:
                    msg = f"__Hi there you have just initiated the authorization process which hardy takes 2 min. Send /auth command to begin.__"
                    await client.send_message(
                        current_client["from_user"].id,
                        f"{msg}",
                        disable_web_page_preview=True,
                    )
                    username = (
                        current_client["from_user"].username
                        if hasattr(current_client["from_user"], "username")
                        else "User"
                    )
                    username = (
                        f"[{username}](tg://user?id={current_client['from_user'].id})"
                    )
                    msg = f"__User {username} has initiated the authorization process, if you suspect this is an error contact suppport.__"
                    m = await client.send_message(
                        current_client["from_chat"].id,
                        f"{msg}",
                        disable_web_page_preview=True,
                    )
                    loop.create_task(delayDelete(m, 20))
                except Exception as ex:
                    logWarning(f"Unable to send auth message : {ex}")

                return await callback_query.answer(
                    f"Authorization intitiated for chat: {current_client['from_chat'].id}.\nPlease open {config.get('BOT_USERNAME')} and send /auth command.",
                    show_alert=True,
                )

            return await callback_query.answer(
                f"Sorry but only chat admins who are not anonymous can authorize the bot, Ask the admin to perform this action.",
                show_alert=True,
            )
        return await callback_query.answer(
            f"Invalid action. Contact admin.", show_alert=True
        )
    except Exception as ex:
        logException(f"Error in on_callback_query: {ex}", True)
