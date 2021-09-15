import asyncio
from utils.Config import Config
from utils.Logger import logException, logWarning, logInfo, logger
from utils.MongoClient import MongoDBClient
from utils.Helper import Helper
from utils.Singleton import Singleton
from utils.SongInfoFetcher import VideoSearch, VideoFetchFromId
from utils.GenerateCover import generate_blank_cover, generate_cover

config = Config()
mongoDBClient = MongoDBClient()
helperClient = Helper()
loop = asyncio.get_event_loop()
__all__ = [
    "config",
    "helperClient",
    "mongoDBClient",
    "logException",
    "logWarning",
    "logInfo",
    "logger",
    "loop",
    "Singleton",
    "VideoSearch",
    "VideoFetchFromId",
    "generate_blank_cover",
    "generate_cover",
]
