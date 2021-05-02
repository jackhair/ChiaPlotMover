import threading
import time
import signal
import os
import shutil
import discord_notify

from datetime import timedelta

# ------------------
# User Configuration
# ------------------
# Update these settings to match your system

# Time interval between jobs
WAIT_TIME_SECONDS = 1800
# Directory you stage your files at
STAGING_DIR = 'R:/'
# Destination to move staged files to
DESTINATION_DIR = "G:/"
# Discord webhook URL for sending Discord messages on job complete
DISCORD_WEBHOOK_URL = ""


class ProgramKilled(Exception):
    pass


def init():
    print(time.ctime())
    print("Checking staging drive: " + STAGING_DIR)

    stagingFiles = os.listdir(STAGING_DIR)
    notifier = discord_notify.Notifier(DISCORD_WEBHOOK_URL)

    # Check if files exist
    if not stagingFiles:
        stagingEmptyMessage = "Staging empty."
        notifier.send(stagingEmptyMessage, print_message=False)
        print(stagingEmptyMessage)
        return

    # Filter files for .plot extension
    filteredFiles = list(filter(lambda k: k.endswith(".plot"), stagingFiles))

    if not filteredFiles:
        noPlotsMessage = "No plots found."
        notifier.send(noPlotsMessage, print_message=False)
        print(noPlotsMessage)
        return

    print("Found " +
          str(len(filteredFiles)) + " plots.")

    for file in filteredFiles:
        fileLocation = STAGING_DIR + file
        fileSizeBytes = os.path.getsize(fileLocation)

        destinationDrive = DESTINATION_DIR
        destinationFileLocation = destinationDrive + file

        print("- " + file)

        print("- Size: " +
              str(fileSizeBytes/1000000) + " MB")

        print("Moving file...")

        shutil.move(fileLocation, destinationFileLocation)

        message = "Moved plot from staging: " + file

        notifier.send(message, print_message=False)
        print(message)

        print("-------------------")

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
    print("Starting staging scheduler.")
    print("Checking drive: " + STAGING_DIR)
    print("Scheduled every: " + str(WAIT_TIME_SECONDS) + " seconds")
    
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
