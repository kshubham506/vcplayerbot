from decorators.must_have_mongo import must_have_mongo
from utils.Logger import logException
from decorators.save_user_chat_db import save_user_chat_in_db
from decorators.message_factory import getMessage
from pyrogram import Client, filters

from utils import logger, mongoDBClient, loop, config, logWarning, logInfo
from decorators.extras import delayDelete, send_message, validate_session_string


def validate_command(parsed_command, auth_docs, filtered_chat):
    _, uuid, api_id, api_hash, session_string = parsed_command
    if not uuid:
        return f"__Invalid uuid: {uuid}. Send /auth to view the correct steps.__"
    if not api_id or api_id.isdecimal() is False:
        return f"__Invalid api_id: {api_id}. Send /auth to view the correct steps.__"
    if not api_hash or len(api_hash) < 5:
        return (
            f"__Invalid api_hash: {api_hash}. Send /auth to view the correct steps.__"
        )
    if not session_string or len(session_string) < 20:
        return f"__Invalid session_string: {session_string}. Send /auth to view the correct steps.__"
    if not filtered_chat:
        return f"__Invalid uuid: {uuid}. Send /auth to view the correct steps.__"
    return None


@Client.on_message(
    filters.command(["auth", "auth@vcplayerbot"]) & ~filters.edited & filters.private,
    group=-1,
)
@must_have_mongo
@save_user_chat_in_db
async def auth(client, message, current_client):
    try:
        parsed_command = message.command
        auth_docs = mongoDBClient.get_temp_auths(current_client["from_user"].id)
        if not auth_docs:
            msg, kbd = getMessage(message, "no-auth-docs")
            return await client.send_message(
                message.chat.id,
                f"{msg}",
                disable_web_page_preview=True,
                reply_markup=kbd,
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
                    m1 = await send_message(
                        client, message.chat.id, f"__Validating...__"
                    )
                    status, reason, _user, id, username = await validate_session_string(
                        api_id, api_hash, session_string
                    )
                    loop.create_task(delayDelete(m1, 5))
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
                        msg = f"__User {cur_username} has completed the authorization process, you can now start using the bot. Send /help for list of commands or send /play to start media playback right now.__"
                        await send_message(client, filtered_chat["chat_id"], f"{msg}")
                        await send_message(
                            client,
                            message.chat.id,
                            f"__✔️ Completed authorization, Check your chat group.__",
                        )
                        mongoDBClient.complete_temp_auth_doc(uuid)
                        loop.create_task(delayDelete(message, 5))
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
                    + f"\nHow to get the api id, api hash or session_string? [Read Here]({config.get('SESSION_STRING_STEPS')})"
                )
                m = await client.send_message(
                    message.chat.id, f"{msg}", disable_web_page_preview=True
                )
                loop.create_task(delayDelete(m, 10 * 60))
    except Exception as ex:
        await send_message(
            client, message.chat.id, f"__Error while authorizing : {ex}__"
        )
        logException(f"Error in auth: {ex}", True)
