from threading import Thread
from datetime import datetime
import logging

from TomatoLeafs.webapp import app
from TomatoLeafs.webapp.files_monitor import monitor


if __name__ == '__main__':
    if app.config["TESTING"] is False:
        logging.info(f"[MONITOR] - [{datetime.now()}] started")
        monitor_thread = Thread(target=monitor, args=()).start()

    app.run(port=8000, debug=True)