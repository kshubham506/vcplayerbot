from typing import Callable
from pyrogram import Client
from utils import logException, mongoDBClient


def must_have_mongo(func: Callable) -> Callable:
    async def decorator(client: Client, incomingPayload):
        try:
            if not mongoDBClient.client:
                return
            return await func(client, incomingPayload)
        except Exception as ex:
            logException(f"Error in must_have_mongo: {ex}")

    return decorator
