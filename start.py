import threading
import time
import signal
import os
import shutil
import discord_notify

from datetime import timedelta
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

# ------------------
# CONFIG
# ------------------
WAIT_TIME_SECONDS = os.environ.get("INTERVAL")
STAGING_DIR = os.environ.get("STAGING")
DESTINATION_DIR = os.environ.get("DESTINATION")
DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")


class ProgramKilled(Exception):
    pass


def sendMessage(message):
    print(f"{time.ctime()} - {message}")

    time.sleep(1)

    if DISCORD_WEBHOOK_URL is not None:
        notifier = discord_notify.Notifier(DISCORD_WEBHOOK_URL)
        notifier.send(message, print_message=False)


def init():
    sendMessage(f"Start check: {STAGING_DIR}")

    stagingFiles = os.listdir(STAGING_DIR)

    # Check if files exist
    if not stagingFiles:
        sendMessage("Staging empty.")
        return

    # Filter files for .plot extension
    filteredFiles = list(filter(lambda k: k.endswith(".plot"), stagingFiles))

    if not filteredFiles:
        sendMessage("No plots found.")
        return

    sendMessage(f"Found {str(len(filteredFiles))} plots.")

    for file in filteredFiles:
        fileLocation = STAGING_DIR + file
        fileSizeBytes = os.path.getsize(fileLocation)

        destinationDrive = DESTINATION_DIR
        destinationFileLocation = destinationDrive + file

        sendMessage(file)
        sendMessage(f"Size: {str(fileSizeBytes/1000000)} MB")
        sendMessage("Moving file...")

        shutil.move(fileLocation, destinationFileLocation)

        sendMessage("Moved plot from staging: " + file)

    return


def signal_handler(signum, frame):
    raise ProgramKilled


class Job(threading.Thread):
    def __init__(self, interval, execute, *args, **kwargs):
        threading.Thread.__init__(self)
        self.daemon = False
        self.stopped = threading.Event()
        self.interval = interval
        self.execute = execute
        self.args = args
        self.kwargs = kwargs

    def stop(self):
        self.stopped.set()
        self.join()

    def run(self):
        while not self.stopped.wait(self.interval.total_seconds()):
            self.execute(*self.args, **self.kwargs)


if __name__ == "__main__":
    # Inform schedule start
    sendMessage("Starting staging scheduler.")
    sendMessage("Staging drive set: " + STAGING_DIR)
    sendMessage("Destination drive set: " + DESTINATION_DIR)
    sendMessage("Schedule interval: " + str(WAIT_TIME_SECONDS) + " seconds")

    # Signal stuff
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)

    # Run initial check
    init()

    # Create and schedule job
    job = Job(interval=timedelta(seconds=WAIT_TIME_SECONDS), execute=init)
    job.start()

    # Graceful program kill
    while True:
        try:
            time.sleep(1)
        except ProgramKilled:
            print("Program killed: running cleanup code.")
            job.stop()
            break
