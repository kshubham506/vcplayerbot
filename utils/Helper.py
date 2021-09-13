from utils.Config import Config
from requests_futures.sessions import FuturesSession
from utils.Logger import *
from utils.ExtractLinks import ExtractLinks
import re


class Helper:
    def __init__(
        self,
    ) -> None:
        self.config = Config()
        self.extracturls = ExtractLinks()

    def getUrls(self, message):
        try:
            return self.extracturls.extractLinks(message)
        except Exception as ex:
            logException("Error in geturls : {}".format(ex))

    def isEmpty(self, message):
        try:
            return message is None or len(message.strip()) == 0
        except Exception as ex:
            logException("Error in isEmpty : {}".format(ex))
            raise Exception(ex)

    def checkForArguments(self, command, arg):
        try:
            if arg == "IS_VIDEO":
                return re.search(" -video", command) is not None
            elif arg == "REPEAT":
                return re.search(" -repeat", command) is not None
            elif arg == "SILENT":
                return re.search(" -silent", command) is not None
            elif arg == "ONLY_AUDIO":
                return re.search(" -audio", command) is not None
            elif arg == "LIP_SYNC":
                return re.search(" -lipsync", command) is not None
            elif arg == "RES":
                res = re.findall(" -res\w+", command)
                if len(res) > 0:
                    quality = re.findall("\d+", res[0])
                    return quality[0] if len(quality) > 0 else None
            elif arg == "NAME":
                return re.sub(
                    "\/play@\w+|\/play|-video|-repeat|-silent|audio|lipsync|-res\w+",
                    "",
                    command,
                ).strip()
            else:
                raise Exception("Invalid arg")
        except Exception as ex:
            logException("Error in checkForArguments : {}".format(ex))

    def sendWebhook(self, msg, hashTag=None):
        try:
            if (
                self.config.get("env") == "local"
                or self.config.get("webhookUrl") is None
            ):
                return
            session = FuturesSession()

            msg = "<b>{}[{}]</b>\n{}".format(
                self.config.get("env"), self.config.get("server"), msg
            )
            payload = {
                "message": msg,
                "source": self.config.get("source"),
                "env": self.config.get("env"),
            }
            if hashTag is not None:
                payload["hashTag"] = hashTag

            session.post(
                self.config.get("webhookUrl"),
                data=payload,
                headers={"authorization": self.config.get("WEBHOOK_AUTH")},
            )
        except Exception as ex:
            print("Error in sendWebhook : {}".format(ex))
