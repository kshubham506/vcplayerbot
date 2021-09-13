from loguru import logger
from datetime import datetime
import logging
from r7insight import R7InsightHandler

from utils.Config import Config
from utils.Helper import Helper

config = Config()
helperClient = Helper()

timeName = datetime.now().strftime("%d-%m-%Y")
fmt = "{time} | {level: <8} | {name: ^15} | {function: ^15} | {line: >3} | {message}"
logger.add(
    "Logs/log-{}.log".format(timeName),
    level="INFO",
    format=fmt,
    rotation="1 days",
    retention="1 days",
    encoding="utf8",
)
logger.opt(lazy=True)


class InterceptHandler(logging.Handler):
    def emit(self, record):
        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


logging.getLogger("filelock").setLevel(logging.ERROR)
logging.basicConfig(handlers=[InterceptHandler()], level="INFO")

# optional advanced feature, for sending logs to r7
if config.get("env") == "prod":
    if (
        config.get("LOG_INSIGHT_KEY") is not None
        and config.get("LOG_INSIGHT_REGION") is not None
    ):
        r7LogHandler = R7InsightHandler(
            config.get("LOG_INSIGHT_KEY"), config.get("LOG_INSIGHT_REGION")
        )
        logger.add(r7LogHandler)


def logInfo(message):
    try:
        logger.info(f'{config.get("server")}=>{message}')
    except Exception as ex:
        logger.exception(ex)


def logWarning(message):
    try:
        logger.warning(f'{config.get("server")}=>{message}')
    except Exception as ex:
        logger.exception(ex)


def logException(message, *args):
    try:
        sendWebhook = True
        if len(args) > 0:
            (sendWebhook,) = args

        logger.exception(f'{config.get("server")}=>{message}')

        if sendWebhook is True:
            helperClient.sendWebhook(f"{message}")
    except Exception as ex:
        logger.exception(ex)
