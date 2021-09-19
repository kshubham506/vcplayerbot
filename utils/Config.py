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
                **dotenv_values(".env"),
                **os.environ,
            }
            self.config["env"] = "prod"
        else:
            self.config = {
                **dotenv_values(".env.local"),
                **os.environ,
            }
            self.config["env"] = "local"

        self.config["source"] = "tgcalls"

        self.config["server"] = "tgserver-beta"

        self.config["ALLOWED_CHAT_TYPES"] = [
            "channel",
            "groups",
            "group",
            "supergroup",
            "supergroups",
            "megagroup",
        ]

        ## no need to modify these
        if "BOT_URL" not in self.config or not self.config["BOT_URL"]:
            self.config["BOT_URL"] = "https://t.me/vcplayerbot"
        if "PARENT_URL" not in self.config or not self.config["PARENT_URL"]:
            self.config["PARENT_URL"] = "https://t.me/sktechhub"
        if "SUPPORT_GROUP" not in self.config or not self.config["SUPPORT_GROUP"]:
            self.config["SUPPORT_GROUP"] = "https://t.me/voicechatsupport"
        if "GITHUB_REPO" not in self.config or not self.config["GITHUB_REPO"]:
            self.config["GITHUB_REPO"] = "https://github.com/kshubham506/vcplayerbot"
        self.config["SUDO_USER"] = [563365858]
        self.config["PROMOTIONAL_DATA"] = {}

        """
        The below values you can specify as env variables or modify here directly
        """
        # number which dentores how many simultaneous playbacks can run
        if (
            "SIMULTANEOUS_CALLS" not in self.config
            or not self.config["SIMULTANEOUS_CALLS"]
        ):
            self.config["SIMULTANEOUS_CALLS"] = 5

        # text to add at footer of each play message (if any)
        if "PLAYBACK_FOOTER" not in self.config:
            self.config["PLAYBACK_FOOTER"] = ""

        # number of songs that can be added to queue
        if "PLAYLIST_SIZE" not in self.config or not self.config["PLAYLIST_SIZE"]:
            self.config["PLAYLIST_SIZE"] = 10

        # max duration for any song/video
        if (
            "ALLOWED_SONG_DURATION_IN_SEC" not in self.config
            or not self.config["ALLOWED_SONG_DURATION_IN_SEC"]
        ):
            self.config["ALLOWED_SONG_DURATION_IN_SEC"] = 13 * 60

        # readme file/url listing steps to generate session string
        if (
            "SESSION_STRING_STEPS" not in self.config
            or not self.config["SESSION_STRING_STEPS"]
        ):
            self.config[
                "SESSION_STRING_STEPS"
            ] = "https://github.com/kshubham506/vcplayerbot/blob/master/get_session_string.md"

        # minimum number of members required to access the bot
        if "MIN_MEMBERS_REQUIRED" not in self.config:
            self.config["MIN_MEMBERS_REQUIRED"] = 0

        # default value for new chat: ALLOW_VIDEO
        if "ALLOW_VIDEO" not in self.config:
            self.config["ALLOW_VIDEO"] = True

        # default value for new chat: ALLOW_AUDIO
        if "ALLOW_AUDIO" not in self.config:
            self.config["ALLOW_AUDIO"] = True

        # default value for new chat: ALLOW_OTHERS
        if "ALLOW_YOUTUBE" not in self.config:
            self.config["ALLOW_YOUTUBE"] = True

        # default value for new chat: ALLOW_OTHERS
        if "ALLOW_OTHERS" not in self.config:
            self.config["ALLOW_OTHERS"] = True

        # default value for new chat: MAX_VIDEO_RES
        if "MAX_VIDEO_RES" not in self.config:
            self.config["MAX_VIDEO_RES"] = 1920

        # default value for new chat: MAX_AUDIO_RES
        if "MAX_AUDIO_RES" not in self.config:
            self.config["MAX_AUDIO_RES"] = 1920

        # default value for new chat: ALLOW_REPEAT
        if "ALLOW_REPEAT" not in self.config:
            self.config["ALLOW_REPEAT"] = True

        # should other group be able to add the bot and use it
        # 0 - False , 1 - True
        if "ALLOW_MULTIPLE_CHATS" not in self.config:
            self.config["ALLOW_MULTIPLE_CHATS"] = 1

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
