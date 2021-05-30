
from utils.Config import Config
from requests_futures.sessions import FuturesSession
from utils.Logger import *
from utils.ExtractLinks import ExtractLinks


class Helper:
    def __init__(self, ) -> None:
        self.config = Config()
        self.extracturls = ExtractLinks()

    def getUrls(self, message):
        try:
            return self.extracturls.extractLinks(message)
        except Exception as ex:
            logException("Error in geturls : {}".format(ex))

    def sendWebhook(self, msg, hashTag=None):
        try:
            if self.config.get("env") == "local" or self.config.get("webhookUrl") is None:
                return
            session = FuturesSession()

            msg = "<b>{}[{}]</b>\n{}".format(self.config.get("env"),
                                             self.config.get("server"), msg)
            payload = {"message": msg, "source": self.config.get("source"),
                       "env": self.config.get("env")}
            if hashTag is not None:
                payload['hashTag'] = hashTag

            session.post(self.config.get('webhookUrl'), data=payload, headers={
                "authorization": self.config.get('WEBHOOK_AUTH')})
        except Exception as ex:
            print("Error in sendWebhook : {}".format(ex))
