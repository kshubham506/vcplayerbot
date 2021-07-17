import pymongo
from pymongo.collection import ReturnDocument
from utils.Config import Config
from utils.Logger import *
from utils.Singleton import Singleton


class MongoDBClient(metaclass=Singleton):
    def __init__(self) -> None:
        self.config = Config()
        if self.config.get('MONGO_URL') is None or len(self.config.get('MONGO_URL')) == 0:
            logWarning(
                "MONGO_URL is none, all database features will be disbaled!")
            self.client = None
        else:
            self.client = pymongo.MongoClient(self.config.get('MONGO_URL'))
            self.sktechhub = self.client["sktechhub"]

    def fetchRunTimeData(self):
        try:
            return self.sktechhub.runtime_data.find_one({'service': self.config.get('source')})
        except Exception as ex:
            logException("Error in fetchRunTimeData : {}".format(ex))
            raise Exception(ex)

    def get_all_chats(self):
        try:
            data = self.sktechhub.tgcalls_chats.find({})
            return list(data if data is not None else [])
        except Exception as ex:
            logException(f"Error in get_active_chats : {ex}")

    def add_tgcalls_chats(self, chatInfo):
        try:
            exists = self.sktechhub.tgcalls_chats.find(
                {"chat_id": chatInfo['chat_id']})
            if list(exists) in [None, []]:
                self.sktechhub.tgcalls_chats.insert_one(chatInfo)
                self.config.updateChat(chatInfo, True)
        except Exception as ex:
            logException(f"Error in add_tgcalls_chats : {ex}")

    def add_song_playbacks(self, songInfo, requestedUser, docId):
        try:
            if self.config.get("env") == "prod":
                self.sktechhub.tgcalls_playbacks.insert_one(
                    {'tgcalls_chat': docId, 'song': songInfo, 'requested_by': requestedUser, "updated_at": datetime.now()})
        except Exception as ex:
            logException(
                f"Error in add_song_playbacks : {ex} , {songInfo}, {requestedUser}, {docId}")

    def update_admins(self, chatId, admins):
        try:
            if isinstance(admins, list) is True:
                data = self.sktechhub.tgcalls_chats.find_one_and_update(
                    {'chat_id': chatId}, {'$set': {'admins': admins}}, return_document=ReturnDocument.AFTER)
            elif isinstance(admins, dict) is True:
                data = self.sktechhub.tgcalls_chats.find_one_and_update(
                    {'chat_id': chatId}, {'$push': {'admins': admins}}, return_document=ReturnDocument.AFTER)
            else:
                raise Exception(
                    f"Invalid type to add admin : {chatId} , {admins} ")
            self.config.updateChat(data)
        except Exception as ex:
            logException(f"Error in update_admins : {ex}")

    def remove_admins(self, chatId, adminToRemove):
        try:
            if isinstance(adminToRemove, dict) is True:
                data = self.sktechhub.tgcalls_chats.find_one_and_update(
                    {'chat_id': chatId}, {'$pull': {'admins': {'chat_id': adminToRemove['chat_id']}}}, return_document=ReturnDocument.AFTER)
            else:
                raise Exception(
                    f"Invalid type to remove admin : {chatId} , {adminToRemove} ")
            self.config.updateChat(data)
        except Exception as ex:
            logException(f"Error in remove_admins : {ex}")

    def update_admin_mode(self, chatId, newStatus):
        try:
            if isinstance(newStatus, bool) is True:
                data = self.sktechhub.tgcalls_chats.find_one_and_update(
                    {'chat_id': chatId}, {'$set': {'admin_mode': newStatus}}, return_document=ReturnDocument.AFTER)
            else:
                raise Exception(
                    f"Invalid type to update admin mode : {chatId} , {newStatus} ")
            self.config.updateChat(data)
        except Exception as ex:
            logException(f"Error in update_admin_mode : {ex}")

    def add_tgcalls_users(self, userInfo):
        try:
            self.sktechhub.tgcalls_users.replace_one(
                {'chat_id': userInfo['chat_id']}, userInfo, True)
        except Exception as ex:
            logException(f"Error in add_tgcalls_users : {userInfo} ,{ex}")

    def chats_to_disconnect(self):
        try:
            from datetime import timedelta
            agg = [
                {
                    '$match':  {
                        'updated_at': {'$lt': (datetime.now() - timedelta(hours=0, minutes=30))}
                    }
                }, {
                    '$group': {
                        '_id': '$tgcalls_chat'
                    }
                }, {
                    '$lookup': {
                        'from': 'tgcalls_chats',
                        'localField': '_id',
                        'foreignField': '_id',
                        'as': 'chat'
                    }
                }, {
                    '$unwind': {
                        'path': '$chat',
                        'preserveNullAndEmptyArrays': True
                    }
                }
            ]
            if self.config.get("env") == "local":
                agg.append({
                    '$match':  {
                        "chat.testing": True
                    }
                })
            result = self.sktechhub['tgcalls_playbacks'].aggregate(agg)
            return list(result)
        except Exception as ex:
            logException(f"Error in getting chats : {ex}")
