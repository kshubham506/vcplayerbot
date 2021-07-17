from pyrogram import Client, idle
from utils.Config import Config
from callmanager import MusicPlayer, user_app
import signal
import sys
import asyncio
from utils.Logger import *
import os
from dbhandler import handle_db_calls, leaveStaleChats
import time
import threading
import schedule


async def shutdown(signal, loop):
    try:
        logInfo(f"Received exit signal {signal.name}...")

        # close the music player instances
        mp = MusicPlayer()
        await mp.shutdown()

        tasks = [t for t in asyncio.all_tasks() if t is not
                 asyncio.current_task()]

        [task.cancel() for task in tasks]

        logInfo(f"Cancelling {len(tasks)} outstanding tasks")
        await asyncio.gather(*tasks, return_exceptions=True)
        loop.stop()
    except Exception as ex:
        logWarning("Error while closing all tasks : {}".format(ex))


def removeOldFilesImages(path=['images/']):
    try:
        logInfo("Removing old files images")
        removed = []
        olderThan = 1*60*60  # in seconds
        for p in path:
            for f in os.listdir(p):
                file_path = os.path.join(p, f)
                if os.path.isfile(file_path) and os.stat(file_path).st_mtime < (time.time() - olderThan):
                    os.remove(file_path)
                    removed.append(file_path)
        logInfo(f"Removed files : {removed}")

    except Exception as ex:
        logException(f"Error while removing files in scheduler- {ex}", True)
        return []


def removeOldFilesSongs(path=['songs/']):
    try:
        logInfo("Removing old files songs")
        removed = []
        olderThan = 2*60*60  # in seconds
        for p in path:
            for f in os.listdir(p):
                file_path = os.path.join(p, f)
                if os.path.isfile(file_path) and os.stat(file_path).st_mtime < (time.time() - olderThan):
                    os.remove(file_path)
                    removed.append(file_path)
        logInfo(f"Removed files : {removed}")

    except Exception as ex:
        logException(f"Error while removing files in scheduler- {ex}", True)
        return []


def removeStaleClientsScheduler(loop):
    try:
        loop.create_task(leaveStaleChats())
    except Exception as ex:
        logException(f"Error in removeStaleClientsScheduler : {ex}")


"""
method to run scheduler jobs in thread
"""


def run_threaded(job_func, arg):
    job_thread = threading.Thread(target=job_func, args=arg)
    job_thread.start()
    if len(arg) >= 3 and arg[2] is True:
        return schedule.CancelJob


def main():
    loop = None
    bot = None
    try:
        # create the images and song folder if not there
        folders = ['songs', 'images', 'Logs']
        for f in folders:
            if not os.path.exists(f):
                os.makedirs(f)

        loop = asyncio.get_event_loop()

        config = Config()

        if config.get("env") == "prod":
            schedule.every(3).hours.do(
                run_threaded, removeOldFilesSongs, ())
            schedule.every(2).hours.do(
                run_threaded, removeOldFilesImages, ())
            # make user bot leave stale chats only if auto leave mode is on
            if config.get('AUTO_LEAVE') == "on":
                schedule.every(6).hours.do(removeStaleClientsScheduler, loop)
        else:
            pass
            # schedule.every(10).seconds.do(removeStaleClientsScheduler, loop)

        bot = Client(":memory:", api_id=config.get(
            'API_ID'), api_hash=config.get('API_HASH'), bot_token=config.get("BOT_TOKEN"), plugins=dict(root="modules"))

        def sig_handler(signum, frame):
            logException(f"Segmentation Fault : {signum} : {frame}", True)

        signal.signal(signal.SIGSEGV, sig_handler)

        try:
            for signame in {'SIGINT', 'SIGTERM'}:
                s = getattr(signal, signame)
                loop.add_signal_handler(
                    s, lambda s=s: asyncio.create_task(shutdown(s, loop)))
        except NotImplementedError:
            logWarning("Not implemented error : ")

        bot.start()
        user_app.start()

        bot_details = bot.get_me()
        user_app_details = user_app.get_me()

        config.setBotId(bot_details.id)
        config.setHelperActId(user_app_details.id)
        config.setHeleprActUserName(user_app_details.username)

        loop.create_task(handle_db_calls())

        loop.run_forever()
    except KeyboardInterrupt as k:
        logWarning("Client Keyboard Interrupt, Exiting Code")
    except Exception as ex:
        logException(f"Error in main method : {ex}", True)
    finally:
        logException(f"Closed the service :)", True)
        if bot is not None:
            bot.stop()
        if user_app is not None:
            user_app.stop()


if __name__ == "__main__":
    try:
        logInfo(
            "Started the Backend Server For Voice Chat Music Player | A SkTechHub Product")
        main()
    except Exception as ex:
        logException(f"Error in main start : {ex}", True)
    finally:
        logInfo("Closing the service :)")
        sys.exit(0)
