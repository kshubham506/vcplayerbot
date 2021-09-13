from utils import logger, logInfo
import os
import time


@logger.catch
def removeOldFiles(path=["images/"]):
    logInfo("Removing old files")
    removed = []
    olderThan = 2 * 60 * 60  # in seconds
    for p in path:
        for f in os.listdir(p):
            file_path = os.path.join(p, f)
            if os.path.isfile(file_path) and os.stat(file_path).st_mtime < (
                time.time() - olderThan
            ):
                os.remove(file_path)
                removed.append(file_path)
    logInfo(f"Removed files : {removed}")
