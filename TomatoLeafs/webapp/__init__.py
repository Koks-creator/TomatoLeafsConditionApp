from datetime import timedelta
import os
from flask import Flask

from TomatoLeafs.webapp.config import Config


config = Config()

app = Flask(__name__)
app.secret_key = 'elosiema5656531563'
app.config["SESSION_TYPE"] = "filesystem"
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(seconds=config.SESSION_TIME_SECONDS)
app.config["TESTING"] = False


tips_dict = {}
for file in os.listdir(config.TIPS_FILES_PATH):
    class_name, _ = os.path.splitext(file)

    with open(rf"{config.TIPS_FILES_PATH}\{class_name.lower()}.txt", encoding="utf-8") as f:
        content = f.read()

    content = content.split("\n")
    tips_dict[class_name] = content

from TomatoLeafs.webapp import routes
