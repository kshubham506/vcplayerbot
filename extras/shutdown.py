import asyncio
from utils import logger, logInfo


@logger.catch
async def shutdown(signal, loop):
    logInfo(f"Received exit signal {signal.name}...")

    # close the music player instances
    # mp = MusicPlayer()
    # await mp.shutdown()

    tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]

    [task.cancel() for task in tasks]

    logInfo(f"Cancelling {len(tasks)} outstanding tasks")
    await asyncio.gather(*tasks, return_exceptions=True)
    loop.stop()
