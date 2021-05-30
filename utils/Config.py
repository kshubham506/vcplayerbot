from dotenv import dotenv_values
import argparse

from utils.Singleton import Singleton


class Config(metaclass=Singleton):

    def getCLIParser(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("-env", "--Environment",
                            help="Provide environment (local/prod)")
        parser.add_argument("-service", "--Service",
                            help="Provide service name (call)")
        parser.add_argument("-server", "--Server",
                            help="Provide server name (tgserver)")
        return parser

    def __init__(self) -> None:
        self.args = self.getCLIParser().parse_args()

        if self.args.Environment == 'prod':
            self.config = dotenv_values(".env")
            self.config['env'] = "prod"
        else:
            self.config = dotenv_values(".env.local")
            self.config['env'] = "local"

        if self.args.Service == "call":
            self.config['source'] = "tgcalls"
        else:
            print("Invalid Service Name Provided.")
            exit(0)

        self.config['server'] = 'tgserver'

        self.config['ALLOWED_CHAT_TYPES'] = [
            'groups', 'group', 'supergroup', 'supergroups']
        self.config["ACTIVE_CLIENTS"] = []
        self.config["GLOBAL_ADMINS"] = []
        self.config["SIMULTANEOUS_CALLS"] = 5
        self.config['PLAYBACK_FOOTER'] = ''
        self.config['PLAYLIST_SIZE'] = 1
        # chat where restriction of number of simulataneous playbacks is not applicable
        self.config['SUDO_CHAT'] = [-1001468590972]

    def get(self, key):
        return self.config.get(key)

    def getAll(self):
        return self.config

    def setAllowedChatTypes(self,  value):
        self.config['ALLOWED_CHAT_TYPES'] = value

    def setActiveClients(self,  value):
        self.config['ACTIVE_CLIENTS'] = value

    def setExtraData(self, key, value):
        self.config[key] = value

    def saveGlobalAdmins(self, value):
        self.config["GLOBAL_ADMINS"] = value

    def save_simultaneous_calls(self, value):
        self.config["SIMULTANEOUS_CALLS"] = value

    def save_playback_footer(self, value):
        self.config['PLAYBACK_FOOTER'] = value

    def save_playlist_size(self, value):
        self.config['PLAYLIST_SIZE'] = value

    def fetchClient(self, chat_id):
        data = list(
            filter(lambda a: a['chat_id'] == chat_id, self.config["ACTIVE_CLIENTS"]))

        return (None if len(data) == 0 else data[0])

    def getAdminForChat(self, chat_id):
        chat_admins = self.fetchClient(chat_id)
        return self.config["GLOBAL_ADMINS"] + chat_admins.get('admins', []) if chat_admins not in [[], None] else []

    def updateChat(self, chat, updateMissing=False):
        found = False
        for c in self.config["ACTIVE_CLIENTS"]:
            if c['chat_id'] == chat['chat_id']:
                c.update(chat)
                found = True
        if found is False and updateMissing is True:
            self.config["ACTIVE_CLIENTS"].append(chat)
