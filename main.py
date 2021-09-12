from extras.dbhandler import handle_db_calls
from extras.remove_old_files import removeOldFiles
from extras.shutdown import shutdown
from pyrogram import Client
from utils import config, logInfo, logWarning, logException

# from callmanager import MusicPlayer  # , user_app
import signal
import sys
import asyncio
import os
import threading
import schedule


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
        folders = ["songs", "images", "Logs"]
        for f in folders:
            if not os.path.exists(f):
                os.makedirs(f)

        loop = asyncio.get_event_loop()

        if config.get("env") == "prod":
            schedule.every(3).hours.do(run_threaded, removeOldFiles, ())
        else:
            pass

        bot = Client(
            ":memory:",
            api_id=config.get("API_ID"),
            api_hash=config.get("API_HASH"),
            bot_token=config.get("BOT_TOKEN"),
            plugins=dict(root="modules"),
        )

        def sig_handler(signum, frame):
            logException(f"Segmentation Fault : {signum} : {frame}", True)

        signal.signal(signal.SIGSEGV, sig_handler)

        try:
            for signame in {"SIGINT", "SIGTERM"}:
                s = getattr(signal, signame)
                loop.add_signal_handler(
                    s, lambda s=s: asyncio.create_task(shutdown(s, loop))
                )
        except NotImplementedError:
            logWarning("Not implemented error : ")

        bot.start()

        bot_details = bot.get_me()
        config.setBotId(bot_details.id)
        config.setBotUsername(bot_details.username)

        # loop.create_task(handle_db_calls())

        loop.run_forever()
    except KeyboardInterrupt as k:
        logWarning("Client Keyboard Interrupt, Exiting Code")
    except Exception as ex:
        logException(f"Error in main method : {ex}", True)
    finally:
        logException(f"Closed the service :)", True)
        if bot is not None:
            bot.stop()


if __name__ == "__main__":
    try:
        logInfo(
            "Started the Backend Server For Voice Chat Music Player | A SkTechHub Product"
        )
        main()
    except Exception as ex:
        logException(f"Error in main start : {ex}", True)
    finally:
        logInfo("Closing the service :)")
        sys.exit(0)
