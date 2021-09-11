from utils.Logger import logException
from decorators.save_user_chat_db import save_user_chat_in_db
from decorators.message_factory import getMessage
from pyrogram import Client, filters

from utils import logger, mongoDBClient, loop, config, logWarning, logInfo
from decorators.extras import delayDelete


def validate_command(parsed_command, auth_docs, filtered_chat):
    _, uuid, api_id, api_hash, session_string = parsed_command
    if not uuid:
        return f"__Invalid uuid: {uuid}. Send /auth to view the correct steps."
    if not api_id or api_id.isdecimal() is False:
        return f"__Invalid api_id: {api_id}. Send /auth to view the correct steps."
    if not api_hash or len(api_hash) < 5:
        return f"__Invalid api_hash: {api_hash}. Send /auth to view the correct steps."
    if not session_string or len(session_string) < 20:
        return f"__Invalid session_string: {session_string}. Send /auth to view the correct steps."
    if not filtered_chat:
        return f"__Invalid uuid: {uuid}. Send /auth to view the correct steps."
    return None


async def validate_session_string(api_id, api_hash, session_string):
    try:
        user_app = Client(
            session_string,
            api_id=api_id,
            api_hash=api_hash,
        )
        await user_app.start()
        me = user_app.get_me()
        logInfo(f"validated user: {user_app.get_me()}")
        await user_app.stop()
        return True, "", me.id, me.username
    except Exception as ex:
        logException(f"Error in validate_session_string : {ex}")
        return False, str(ex), "", ""


@Client.on_message(
    filters.command(["auth", "auth@vcplayerbot"]) & ~filters.edited & filters.private,
    group=-1,
)
@save_user_chat_in_db
@logger.catch
async def auth(client, message, current_client):
    parsed_command = message.command
    auth_docs = mongoDBClient.get_temp_auths(current_client["from_user"].id)
    if not auth_docs:
        msg, kbd = getMessage(message, "no-auth-docs")
        return await client.send_message(
            message.chat.id, f"{msg}", disable_web_page_preview=True, reply_markup=kbd
        )
    else:
        if len(parsed_command) == 5:
            _, uuid, api_id, api_hash, session_string = parsed_command
            filtered_chat = list(
                filter(lambda a: uuid is not None and a["uuid"] == uuid, auth_docs)
            )
            msg = validate_command(parsed_command, auth_docs, filtered_chat)
            if msg:
                return await client.send_message(
                    message.chat.id, f"{msg}", disable_web_page_preview=True
                )
            else:
                status, reason, id, username = await validate_session_string(
                    api_id, api_hash, session_string
                )
                if status is True:
                    filtered_chat = filtered_chat[0]
                    mongoDBClient.save_user_bot_details(
                        filtered_chat["chat_id"],
                        id,
                        username,
                        api_id,
                        api_hash,
                        session_string,
                    )
                    cur_username = (
                        current_client["from_user"].username
                        if hasattr(current_client["from_user"], "username")
                        else "User"
                    )
                    cur_username = f"[{cur_username}](tg://user?id={current_client['from_user'].id})"
                    msg = f"__User {cur_username} has completed the authorization process, you can now start using the bot. Send /help for list of commands.__"
                    m = await client.send_message(
                        filtered_chat["chat_id"],
                        f"{msg}",
                        disable_web_page_preview=True,
                    )
                    loop.create_task(delayDelete(m, 20))
                else:
                    msg = f"__Failed to save the session string.\n\nReason:__{reason}\n\n`Send /auth to view the correct steps`"
                    return await client.send_message(
                        message.chat.id, f"{msg}", disable_web_page_preview=True
                    )
        else:
            filtered, chat_ids = [], []
            for a in auth_docs:
                if a["chat_id"] not in chat_ids:
                    filtered.append({"chat_id": a["chat_id"], "uuid": a["uuid"]})
            msg = f"**Send one of the commands:\n**"
            for f in filtered:
                msg = (
                    msg
                    + f"\n__For chat: {f['chat_id']}__\n\t\t• `/auth {f['uuid']} API_ID API_HASH session_string`\n"
                )
            msg = (
                msg
                + f"\nHow to get the session_string? [Read Here]({config.get('SESSION_STRING_STEPS')})"
            )
            m = await client.send_message(
                message.chat.id, f"{msg}", disable_web_page_preview=True
            )
            loop.create_task(delayDelete(m, 10 * 60))
