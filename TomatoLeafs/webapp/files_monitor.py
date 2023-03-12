import os
from datetime import datetime
from time import time, sleep
import logging

from TomatoLeafs.webapp.config import Config

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

config = Config()


def get_files():
    images = os.listdir(config.PROCESSED_IMG_TEMP_PATH)
    for image in images:
        yield image


def monitor():
    while True:
        curr_time = time()
        for image in get_files():
            diff = (curr_time - os.path.getmtime(fr"{config.PROCESSED_IMG_TEMP_PATH}\{image}"))//1

            if diff >= config.SESSION_TIME_SECONDS:
                os.remove(fr"{config.PROCESSED_IMG_TEMP_PATH}\{image}")
                logging.info(f"[MONITOR] - [{datetime.now()}] Deleting image: {image} from temp files folder")

        sleep(config.MONITOR_REFRESH_TIME_SECONDS)
