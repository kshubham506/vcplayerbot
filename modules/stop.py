# from pyrogram import Client, filters


# import callmanager
# from helpers.decorators import (
#     chat_allowed,
#     delayDelete,
#     admin_mode_check,
#     send_message,
#     parsePlayCommand,
# )
# from utils.Logger import *


# @Client.on_message(
#     filters.command(["stop", "stop@vcplayerbot"]) & ~filters.edited & ~filters.bot
# )
# @chat_allowed
# @admin_mode_check
# async def stop(client, message, current_client):
#     try:
#         chat_id = message.chat.id
#         logInfo(f"Stop command in chat : {chat_id}")

#         parsed_command = parsePlayCommand(
#             message.text, current_client.get("is_admin", False)
#         )
#         if parsed_command["is_silent"] is True:
#             await delayDelete(message)

#         music_player_instance = callmanager.MusicPlayer()
#         (
#             pytgcalls_instance,
#             err_message,
#         ) = await music_player_instance.createGroupCallInstance(
#             chat_id, current_client, client
#         )
#         if pytgcalls_instance is None:
#             m = await send_message(
#                 client, message.chat.id, f"{err_message}", parsed_command["is_silent"]
#             )
#             if (
#                 m is not None
#                 and current_client.get("remove_messages") is not None
#                 and current_client.get("remove_messages") > 0
#             ):
#                 await delayDelete(m, current_client.get("remove_messages"))
#             return

#         status, resp_message = await pytgcalls_instance.stopPlayBack(False, False)

#         m = await send_message(
#             client, message.chat.id, f"{resp_message}", parsed_command["is_silent"]
#         )
#         if (
#             m is not None
#             and current_client.get("remove_messages") is not None
#             and current_client.get("remove_messages") > 0
#         ):
#             await delayDelete(m, current_client.get("remove_messages"))
#         return

#     except Exception as ex:
#         logException(f"Error in stop: {ex}", True)
