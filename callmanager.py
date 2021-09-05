from helpers.fromatMessages import getMessage
from pyrogram import Client
from pyrogram.errors.exceptions import BotMethodInvalid
from pyrogram.errors.exceptions.bad_request_400 import (
    ChannelInvalid,
    ChannelPrivate,
    InviteHashExpired,
    PeerIdInvalid,
    UserAlreadyParticipant,
)
from pyrogram.errors.exceptions.flood_420 import FloodWait
from pytgcalls import GroupCallFactory
import time
import os
from asyncio import QueueEmpty
import asyncio

from pytgcalls.exceptions import GroupCallNotFoundError
from helpers.queues import queues
from utils.Logger import *
from utils.Config import Config
from utils.MongoClient import MongoDBClient
from pyrogram.raw.functions.phone import LeaveGroupCall
from pyrogram.raw.functions.channels import GetFullChannel


config = Config()
MongoDBClient = MongoDBClient()


user_app = Client(
    config.get("USERBOT_SESSION"),
    api_id=config.get("API_ID"),
    api_hash=config.get("API_HASH"),
)


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(
                Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class GoupCallInstance(object):
    def __init__(self, chat_id, mongo_doc, client=None):
        self.client = user_app
        self.bot_client = client
        self.mongo_doc = mongo_doc
        self.chat_id = chat_id
        self.pytgcalls = GroupCallFactory(
            self.client, GroupCallFactory.MTPROTO_CLIENT_TYPE.PYROGRAM
        ).get_group_call()
        self.active = False
        self.status = None
        self.songs = []
        self.playingFile = None
        self.repeatCount = 1
        self.currentRepeatCount = 0

        self.logInfo = lambda msg: logInfo(f"{self.chat_id}=>{msg}")
        self.logWarn = lambda msg: logWarning(f"{self.chat_id}=>{msg}")
        self.logException = lambda msg, send: logException(
            f"{self.chat_id}=>{msg}", send
        )

    def is_connected(self):
        return self.pytgcalls.is_connected

    async def start_playback(self, songInfo, requested_by=""):
        try:
            self.logInfo(
                f"Starting the playback in chat : video : {songInfo['is_video']}, url : {songInfo['link']}"
            )
            try:
                if self.is_connected():
                    await self.pytgcalls.stop()
            except Exception as ex:
                pass
            try:
                await self.pytgcalls.join(self.chat_id)
                if songInfo["is_video"] is False:
                    await self.pytgcalls.start_audio(songInfo["link"])
                else:
                    await self.pytgcalls.start_video(songInfo["link"])
            except GroupCallNotFoundError as ex:
                msg, kbd = getMessage(None, "start-voice-chat")
                return msg
            except Exception as e:
                return f"✖️ **Error while starting the playback:** __{e}__"

            self.songs.append(
                {
                    "song": songInfo,
                    "requested_by": requested_by,
                    "time": time.time(),
                }
            )
            self.status = "playing"
            self.active = True
            return True
        except Exception as ex:
            self.logException(f"Error while starting the playback: {ex}", True)
            return f"**__{ex}__**\n\n__Please add the heleper account `[` {config.get('HELPER_ACT')} `]` in this chat and then send the command again.__"

    async def stopPlayBack(self, fromHandler=False, sendMessage=False):
        try:
            self.logInfo(
                f"Stopping the playback : fromHandler : {fromHandler} ")

            for s in self.songs:
                try:
                    if s.get("file") is not None and os.path.exists(s.get("file")):
                        os.remove(s.get("file"))
                except Exception as ex:
                    self.logException(
                        f"Error while removing the file : {s.get('file')}", True
                    )

            self.songs = []
            self.active = False
            self.status = "stopped"
            try:
                queues.clear(self.chat_id)
            except QueueEmpty:
                pass

            if fromHandler is False:
                try:
                    await self.pytgcalls.stop()
                except Exception as ex:
                    logWarning(
                        f"Can be ignored : pytgcalls.stop :{ex} , {self.chat_id}"
                    )

            await asyncio.sleep(0.1)
            resp_message = "**Playback ended and thank you 🙏🏻 for trying and testing the service.**\n__Do give your feedback/suggestion @sktechhub_chat.__"
            if sendMessage is True and self.bot_client is not None:
                resp_message = "**Playback ended `[If you were in middle of a song and you are getting this message then this has happended due to a deployement. You can play again after some time.]`**\n\n__Thank you for trying and do give your feedback/suggestion @sktechhub_chat.__"
                await self.bot_client.send_message(self.chat_id, f"{resp_message}")
            return True, resp_message
        except BotMethodInvalid as bi:
            self.logWarn(f"Expected error while stopping the playback : {bi}")
            return False, f"**__Error while stopping : {bi}__**"
        except Exception as ex:
            self.logException(f"Error while stopping the playback: {ex}", True)
            return False, f"**__Error while stopping : {ex}__**"


class MusicPlayer(metaclass=Singleton):
    def __init__(self):
        self.group_calls = {}
        self.SIMULTANEOUS_CALLS = config.get("SIMULTANEOUS_CALLS")

    def cleanTheGroupCallDict(self):
        try:
            new_gc = {}
            for chat_id, gc_instance in self.group_calls.items():
                if gc_instance.active is True:
                    new_gc[chat_id] = gc_instance
            logInfo(
                f"cleanTheGroupCallDict : New {len(new_gc)} , old : {len(self.group_calls)}"
            )
            self.group_calls = new_gc
        except Exception as ex:
            logException(f"Error in cleanTheGroupCallDict {ex}", True)

    def createGroupCallInstance(self, chat_id, mongo_doc, client, force=False):
        try:
            logInfo(
                f"Call for Creating new group call instance : {chat_id} {len(self.group_calls)}"
            )
            self.cleanTheGroupCallDict()
            if self.group_calls.get(chat_id) is not None:
                logInfo(f"GroupCall Instance already exists.")
                return self.group_calls.get(chat_id), ""
            else:
                # check if it can be created
                if (
                    chat_id not in config.get("SUDO_CHAT")
                    and len(self.group_calls) >= self.SIMULTANEOUS_CALLS
                    and force is False
                ):
                    return (
                        None,
                        f"**__😖 Sorry but currently the service is being used in `{len(self.group_calls)}` groups/channels and currently due to lack of resource we support at max `{self.SIMULTANEOUS_CALLS}` simultaneous playbacks.__**",
                    )
                logInfo(
                    f"Creating new group call instance : {chat_id} {len(self.group_calls)}"
                )
                gc = GoupCallInstance(chat_id, mongo_doc, client)
                self.group_calls[chat_id] = gc
                return gc, ""

        except Exception as ex:
            logException(f"Error while getting group call {ex}", True)
            return (
                None,
                "**__🙄 Unexpected Error, Be assured our best minds have been notified and they are working on it.__**",
            )

    async def shutdown(self):
        try:
            for chat_id, gc in self.group_calls.items():
                try:
                    if gc is not None and gc.active is True:
                        await gc.stopPlayBack(False, True)
                except Exception as ex:
                    logException(
                        f"Error while shutting down {chat_id},  {ex}", True)

        except Exception as ex:
            logException(
                f"Error while shutting down all instances of music player {ex}", True
            )
