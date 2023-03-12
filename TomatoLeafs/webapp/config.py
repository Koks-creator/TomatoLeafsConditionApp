import os


class Config:
    def __init__(self):
        self.BASE_PATH = os.path.dirname(__file__)
        self.MODELS_PATH = rf"{self.BASE_PATH}/model"
        self.PROCESSED_IMG_TEMP_PATH = rf"{self.BASE_PATH}/static/images/tempImages"
        self.TIPS_FILES_PATH = rf"{self.BASE_PATH}/tips"
        self.SESSION_TIME_SECONDS = 1200
        self.MONITOR_REFRESH_TIME_SECONDS = 30
        self.CONFIDENCE_THRESHOLD = .1
        self.NMS_THRESHOLD = .5
