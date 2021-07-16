from pyrogram import Client
from pyrogram.errors.exceptions import BotMethodInvalid
from pyrogram.errors.exceptions.bad_request_400 import ChannelInvalid, ChannelPrivate, InviteHashExpired, PeerIdInvalid, UserAlreadyParticipant
from pyrogram.errors.exceptions.flood_420 import FloodWait
from pytgcalls import GroupCall
import time
import os
from asyncio import QueueEmpty
import asyncio
from helpers.queues import queues
from utils.Logger import *
from utils.Config import Config
from utils.MongoClient import MongoDBClient
from pyrogram.raw.functions.phone import LeaveGroupCall
from pyrogram.raw.functions.channels import GetFullChannel


config = Config()
MongoDBClient = MongoDBClient()


user_app = Client(config.get('USERBOT_SESSION'), api_id=config.get(
    'API_ID'), api_hash=config.get('API_HASH'))


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(
                Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class GoupCallInstance(object):
    def __init__(self, chat_id, mongo_doc, client=None):
        self.client = client
        self.bot_client = client
        self.mongo_doc = mongo_doc
        self.chat_id = chat_id
        self.pytgcalls = GroupCall(self.client)
        self.active = False
        self.status = None
        self.songs = []
        self.playingFile = None
        self.repeatCount = 1
        self.currentRepeatCount = 0

        self.logInfo = lambda msg: logInfo(f"{self.chat_id}=>{msg}")
        self.logWarn = lambda msg: logWarning(f"{self.chat_id}=>{msg}")
        self.logException = lambda msg, send: logException(
            f"{self.chat_id}=>{msg}", send)

        @self.pytgcalls.on_playout_ended
        async def on_stream_end(gc: GroupCall, *args) -> None:
            try:
                chat_id = gc.full_chat.id
                logInfo(
                    f"Playout ended, skipping to next song, current file which ended : {args}")
                self.currentRepeatCount = self.currentRepeatCount + 1
                if self.repeatCount > 1 and self.currentRepeatCount < self.repeatCount:
                    logInfo(
                        f"Resatrting the playout : Loop : {self.repeatCount} ,Current Count : {self.currentRepeatCount}")
                    self.pytgcalls.restart_playout()
                    return
                await self.skipPlayBack()
            except Exception as ex:
                logException(f"Error in on_stream_end: {ex}", True)

        @self.pytgcalls.on_network_status_changed
        async def on_network_changed(gc: GroupCall, is_connected: bool):
            try:
                logInfo(f"changing status to : {is_connected}")
                chat_id = gc.full_chat.id
                if is_connected is True:
                    self.active = True
                    self.status = "playing"
                else:
                    await self.stopPlayBack(fromHandler=True)
                logInfo(f"status changed : {chat_id} {is_connected}")
            except Exception as ex:
                logException(f"Error in on_network_changed : {ex}", True)

    async def changeClient(self, client):
        try:
            self.logInfo(f"Changed client : {client}")
            self.client = client
            self.pytgcalls.client = client
        except Exception as ex:
            logException(f"Changing client error : {ex}")

    async def changeFile(self, fileName, songInfo, requester, oldFileName=None):
        try:
            self.logInfo(f"Changed file to : {fileName}")
            self.currentRepeatCount = 0
            self.playingFile = fileName
            self.pytgcalls.input_filename = fileName
            try:
                if oldFileName is not None and os.path.exists(oldFileName):
                    os.remove(oldFileName)
            except Exception as ex:
                self.logException(
                    f"Error while removing the file{oldFileName} : {ex}", True)
            if MongoDBClient.client is not None:
                MongoDBClient.add_song_playbacks(
                    songInfo, requester, self.mongo_doc['_id'])
        except Exception as ex:
            logException(f"Error in changeFile : {ex}", True)

    def is_connected(self):
        return self.pytgcalls.is_connected

    async def getCurrentCall(self):
        self.logInfo(f"Making call to get current calls in the chat.")
        return await self.pytgcalls.get_group_call(self.chat_id)

    async def preCheck(self, botClient, useClient):
        try:
            await botClient.get_chat_member(
                chat_id=self.chat_id,
                user_id=config.get('HELPER_ACT_ID')
            )
            return True
        except PeerIdInvalid:
            return True
        except Exception as ex:
            logWarning(f"Error while checkign if helper act is present : {ex}")
        try:
            invitelink = await botClient.export_chat_invite_link(self.chat_id)
            await asyncio.sleep(0.0)
        except Exception as ex:
            logWarning(
                f"Can ignore this => export_chat_invite_link : {self.chat_id} {ex}")
            return f"🕵️‍♀️**Oops, add the bot as an admin in the chat and grant it all permissions.**"
        try:
            await useClient.join_chat(invitelink)
            return True
        except UserAlreadyParticipant:
            return True
        except InviteHashExpired as ie:
            logWarning(
                f"Can ignore this => User is denied : {self.chat_id} {ie}")
            return f"__Error while adding helper account `[` {config.get('HELPER_ACT')} `]` in chat.__\n\n**__Make sure the helper account is not in removed users list.__**"
        except FloodWait as fe:
            logWarning(
                f"Can ignore this => User is denied : {self.chat_id} {fe}")
            return f"__Flood Wait Error while adding helper account `[` {config.get('HELPER_ACT')} `]` in chat.__\n\n**__please wait {fe.x} sec or add the helper accoutn manually.__**"
        except Exception as ex:
            logWarning(
                f"Can ignore this =>  Error : {self.chat_id} {ex}")
            return f"__Error while adding helper account `[` {config.get('HELPER_ACT')} `]` in chat.__\n\n**__{ex}__**"

    async def start_playback(self, fileName, songInfo, requested_by):
        try:
            self.logInfo(
                f"Starting the playback in chat : current song queue : {self.songs}")
            try:
                await self.pytgcalls.start(self.chat_id)
            except Exception as e:
                return f"✖️ **Error while starting the playback:** __{e}__"

            self.songs.append(
                {"file": fileName, "song": songInfo, "requested_by": requested_by, "time": time.time()})
            self.status = "playing"
            self.active = True
            return True
        except Exception as ex:
            self.logException(f"Error while starting the playback: {ex}", True)
            return f"**__{ex}__**\n\n__Please add the heleper account `[` {config.get('HELPER_ACT')} `]` in this chat and then send the command again.__"

    async def addSongsInQueue(self, fileName, songInfo, requested_by):
        try:
            self.logInfo(
                f"Adding song to the queue : {songInfo} , {fileName}")
            if queues.size(self.chat_id) >= config.get('PLAYLIST_SIZE'):
                return True, f"✖️**__Currently at most {config.get('PLAYLIST_SIZE')} songs can be added in queue. Please try again after some songs end.__**"
            await queues.put(self.chat_id, file=fileName, song=songInfo, requested_by=requested_by)
            self.songs.append(
                {"file": fileName, "song": songInfo, "requested_by": requested_by, "time": time.time()})
            req_by = f"[{requested_by['title']}](tg://user?id={requested_by['chat_id']})"
            return True, f"**✅ Added to queue.**\n**Name:** `{(songInfo['title'].strip())[:20]}`\n**Requester:** {req_by}"
        except Exception as ex:
            self.logException(f"Error while addSongsInQueue: {ex}", True)
            return False, "**__Error while adding song in the queue : {ex}.__**"

    async def skipPlayBack(self, fromCommand=False):
        try:
            self.logInfo(
                f"Skipping the playback : from handler : {not fromCommand} ")
            queues.task_done(self.chat_id)
            if queues.is_empty(self.chat_id) is True or len(self.songs) == 0:
                if fromCommand is False:
                    await self.stopPlayBack()
                return False, f"**__😬 There are no songs waiting in queue, If you want to stop send /stop.__**"
            else:
                old_file = self.songs[0].get('file')
                self.songs.pop(0)
                new_song = queues.get(self.chat_id)
                await self.changeFile(
                    new_song["file"], new_song["song"], new_song['requested_by'], old_file)
                return True, f"**__Succesfully skipped the song.__**\n\n**Now Playing ▶️** `{new_song['song']['title']}`"
        except Exception as ex:
            self.logException(f"Error while skipPlayBack: {ex}", True)
            return False, f"**__Error while skipping : {ex}__**"

    async def stopPlayBack(self, fromHandler=False, sendMessage=False, force=False):
        try:
            self.logInfo(
                f"Stopping the playback : fromHandler : {fromHandler} ")
            # delete all downloaded songs in queue
            for s in self.songs:
                try:
                    if s.get("file") is not None and os.path.exists(s.get("file")):
                        os.remove(s.get("file"))
                except Exception as ex:
                    self.logException(
                        f"Error while remving the file : {s.get('file')}", True)

            self.songs = []
            self.active = False
            self.status = 'stopped'
            try:
                queues.clear(self.chat_id)
            except QueueEmpty:
                pass

            if fromHandler is False:
                try:
                    await self.pytgcalls.leave_current_group_call()
                except Exception as ex:
                    logWarning(
                        f"Can be ignored : leave_current_group_call :{ex} , {self.chat_id}")
                finally:
                    await asyncio.sleep(0.1)
                try:
                    if self.is_connected() is True:
                        await self.pytgcalls.stop()
                except Exception as ex:
                    logWarning(
                        f"Can be ignored : pytgcalls.stop :{ex} , {self.chat_id}")
                finally:
                    # await asyncio.sleep(0.1)
                    pass
                if force is True:
                    try:
                        input_peer = await self.client.resolve_peer(self.chat_id)
                        chat = await self.client.send(GetFullChannel(channel=input_peer))
                        leave_call = LeaveGroupCall(call=chat.full_chat.call,
                                                    source=506)
                        await self.client.send(leave_call)
                    except Exception as ex:
                        logWarning(f"Failed to force leave :{ex}")

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

    async def getCurrentInfo(self, userId):
        try:
            self.logInfo(
                f"Getting current info : {self.status}")
            info = f"**Is Active [ {self.chat_id} ] :** `{self.active}` {'**[** `'+self.songs[0].get('song').get('title')+'` **]**' if len(self.songs)>0 else ''}"
            info = info + \
                f"\n**Loop:** `{self.repeatCount if self.repeatCount>1 else 'OFF'}`"
            isEmpty = queues.is_empty(self.chat_id)
            if isEmpty is True or len(self.songs) == 0:
                info = info + f"\n\n__No songs in queue.__"
            else:
                info = info + f"\n\n**Upcoming:**\n"
                sliced_songs = self.songs[1:]
                for i in range(len(sliced_songs)):
                    info = info + \
                        f"**{i+1}.** `{sliced_songs[i].get('song').get('title')}`\n"

            if userId in [i['chat_id'] for i in config.get('GLOBAL_ADMINS')]:
                info = info + "\n\n**Admin View:**"
                music_player = MusicPlayer()
                count = 1
                for chat_id, gc_instance in music_player.group_calls.items():
                    info = info + \
                        f"\n{count}. {chat_id} - **Active:** `{gc_instance.active}` **Status:** `{gc_instance.status}`"
                    info = info + \
                        f" **Queue:** `{len(gc_instance.songs) if gc_instance.songs is not None else None }` , **Loop:** `{self.repeatCount if self.repeatCount>1 else 'OFF'}`"
                    count = count+1
            return True, f"{info}"
        except Exception as ex:
            self.logException(f"Error in getCurrentInfo : {ex}", True)
            return False, f"**__Error while fetching the info : {ex}__**"


class MusicPlayer(metaclass=Singleton):
    def __init__(self):
        self.group_calls = {}
        self.SIMULTANEOUS_CALLS = config.get('SIMULTANEOUS_CALLS')

    def cleanTheGroupCallDict(self):
        try:
            new_gc = {}
            for chat_id, gc_instance in self.group_calls.items():
                if gc_instance.active is True:
                    new_gc[chat_id] = gc_instance
            logInfo(
                f"cleanTheGroupCallDict : New {len(new_gc)} , old : {len(self.group_calls)}")
            self.group_calls = new_gc
        except Exception as ex:
            logException(f"Error in cleanTheGroupCallDict {ex}", True)

    def createGroupCallInstance(self, chat_id, mongo_doc, client, force=False):
        try:
            logInfo(
                f"Call for Creating new group call instance : {chat_id} {len(self.group_calls)}")
            self.cleanTheGroupCallDict()
            if self.group_calls.get(chat_id) is not None:
                logInfo(f"GroupCall Instance already exists.")
                return self.group_calls.get(chat_id), ""
            else:
                # check if it can be created
                if chat_id not in config.get('SUDO_CHAT') and len(self.group_calls) >= self.SIMULTANEOUS_CALLS and force is False:
                    return None, f"**__😖 Sorry but currently the service is being used in `{len(self.group_calls)}` groups/channels and currently due to lack of resource we support at max `{self.SIMULTANEOUS_CALLS}` simultaneous playbacks.__**"
                logInfo(
                    f"Creating new group call instance : {chat_id} {len(self.group_calls)}")
                gc = GoupCallInstance(chat_id, mongo_doc, client)
                self.group_calls[chat_id] = gc
                return gc, ""

        except Exception as ex:
            logException(f"Error while getting group call {ex}", True)
            return None,  "**__🙄 Unexpected Error, Be assured our best minds have been notified and they are working on it.__**"

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
                f"Error while shutting down all instances of music player {ex}", True)
