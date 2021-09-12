from dotenv import dotenv_values
import argparse
import os

from utils.Singleton import Singleton


class Config(metaclass=Singleton):
    def getCLIParser(self):
        parser = argparse.ArgumentParser()
        parser.add_argument(
            "-env", "--Environment", help="[optional]Provide environment (local/prod)"
        )
        return parser

    def __init__(self) -> None:
        self.args = self.getCLIParser().parse_args()

        if self.args.Environment == "prod":
            self.config = {
                **dotenv_values(".env.common"),
                **dotenv_values(".env"),
                **os.environ,
            }
            self.config["env"] = "prod"
        else:
            self.config = {
                **dotenv_values(".env.common"),
                **dotenv_values(".env.local"),
                **os.environ,
            }
            self.config["env"] = "local"

        self.config["source"] = "tgcalls"

        self.config["server"] = "tgserver"

        self.config["ALLOWED_CHAT_TYPES"] = [
            "channel",
            "groups",
            "group",
            "supergroup",
            "supergroups",
            "megagroup",
        ]

        # number which dentores how many simultaneous playbacks can run
        if "SIMULTANEOUS_CALLS" not in self.config:
            self.config["SIMULTANEOUS_CALLS"] = 5

        # text to add at footer of each play message (if any)
        if "PLAYBACK_FOOTER" not in self.config:
            self.config["PLAYBACK_FOOTER"] = ""

        # number of songs that can be added to queue
        if "PLAYLIST_SIZE" not in self.config:
            self.config["PLAYLIST_SIZE"] = 10

        # max duration for any song/video
        if "ALLOWED_SONG_DURATION_IN_SEC" not in self.config:
            self.config["ALLOWED_SONG_DURATION_IN_SEC"] = 15 * 60

        # readme file/url listing steps to generate session string
        if "SESSION_STRING_STEPS" not in self.config:
            self.config[
                "SESSION_STRING_STEPS"
            ] = "https://github.com/kshubham506/vcplayerbot/blob/master/get_session_string.md"

        # minimum number of members required to access the bot
        if "MIN_MEMBERS_REQUIRED" not in self.config:
            self.config["MIN_MEMBERS_REQUIRED"] = 50

        # should other group be able to add the bot and use it
        # 0 - False , 1 - True
        if "ALLOW_MULTIPLE_CHATS" not in self.config:
            self.config["ALLOW_MULTIPLE_CHATS"] = 0

    def get(self, key):
        return self.config.get(key)

    def getAll(self):
        return self.config

    def setExtraData(self, key, value):
        self.config[key] = value

    def setBotId(self, value):
        self.config["BOT_ID"] = value

    def setBotUsername(self, value):
        self.config["BOT_USERNAME"] = value
