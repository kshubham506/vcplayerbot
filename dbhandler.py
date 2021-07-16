from callmanager import user_app
from utils.Logger import *
import asyncio
from utils.MongoClient import MongoDBClient
from utils.Config import Config
from bson import json_util
import asyncio
import schedule
from pyrogram.errors.exceptions.bad_request_400 import UserNotParticipant

mongo_client = MongoDBClient()
config = Config()


async def handle_db_calls():
    while mongo_client.client is not None:
        try:
            # for runtime data
            run_data = mongo_client.fetchRunTimeData()
            # logInfo(f"Making call to fetch runtime data")
            if run_data is not None:
                if run_data.get("alowed_chat_types") not in [None]:
                    config.setAllowedChatTypes(
                        run_data.get("alowed_chat_types"))
                if run_data.get("global_admins") not in [None]:
                    config.saveGlobalAdmins(run_data.get("global_admins"))
                if isinstance(run_data.get("simultaneous_calls"), int) is True:
                    config.save_simultaneous_calls(
                        run_data.get("simultaneous_calls"))
                if isinstance(run_data.get("playlist_size"), int) is True:
                    config.save_playlist_size(
                        run_data.get("playlist_size"))
                if run_data.get("playback_footer") not in [None, '']:
                    config.save_playback_footer(
                        run_data.get("playback_footer"))
                else:
                    config.save_playback_footer('')
                if run_data.get("auto_leave") in ["on", "off"]:
                    config.set_auto_leave_mode(
                        run_data.get("auto_leave"))
            else:
                logWarning("DB handler runtime data is none")

            # fetch active clients
            active_clients = mongo_client.get_all_chats()
            # logInfo(
            #     f"Making call to fetch active clients : {len(active_clients)}")
            config.setActiveClients(active_clients)
            schedule.run_pending()
        except Exception as ex:
            logException(f"Error in handle_db_calls: {ex}", True)
        finally:
            if config.get("env") == "local":
                await asyncio.sleep(5)
            else:
                await asyncio.sleep(30)


async def leaveStaleChats():
    try:
        left = []
        failed = []
        distinct_docs = mongo_client.chats_to_disconnect()
        for chat in distinct_docs:
            try:
                chat_id = None
                c = chat.get("chat")
                if c is not None:
                    chat_id = c.get("chat_id")
                    await user_app.leave_chat(chat_id)
                    left.append(chat_id)
                    await asyncio.sleep(5)
            except UserNotParticipant as e:
                left.append(chat_id)
            except Exception as ex:
                failed.append(chat_id)
                logWarning(f"Error in leave chat inside loop {ex}")
        logException(f"Left the chats : Done {left} , Failed : {failed} ")
    except Exception as ex:
        logException(f"Error in leaveStaeChats , {ex}", True)
