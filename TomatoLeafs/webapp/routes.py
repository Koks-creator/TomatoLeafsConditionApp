from time import time
import os
from flask import render_template, session, redirect, url_for, flash, request
from PIL import Image
import cv2
import numpy as np

from TomatoLeafs.webapp import app, tips_dict
from TomatoLeafs.webapp.forms import MainForm
from TomatoLeafs.webapp.detector import Detector
from TomatoLeafs.webapp.config import Config

config = Config()
MODEL_PATH = config.MODELS_PATH


@app.route("/", methods=["GET", "POST"])
def home():
    form = MainForm()

    if not app.config["TESTING"]:
        form_validation = form.validate_on_submit()
    else:
        form_validation = request.method == 'POST'

    if form_validation:
        image_raw = form.image.data

        # this if is made to prevent errors when using not allowed file extension in testing mode
        if os.path.splitext(form.image.data.filename)[1] in (".png", ".jpg", ".jpeg"):

            img = Image.open(image_raw)
            img = np.array(img)
            img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

            detector = Detector(
                classes_file_path=rf"{MODEL_PATH}/classes.txt",
                weights_file_path=rf"{MODEL_PATH}/yolov3_training_last.weights",
                config_file_path=rf"{MODEL_PATH}/yolov3_testing.cfg",
                confidence_threshold=config.CONFIDENCE_THRESHOLD,
                nms_threshold=config.NMS_THRESHOLD
            )

            detections = detector.detect(img)
            if detections:
                img, counter, most_common, healthy_num, diseased_num, healthy_perc, status = \
                    detector.draw_detections(img, detections)

                filename = f"{time()}_processed.png"
                cv2.imwrite(rf"{config.PROCESSED_IMG_TEMP_PATH}\{filename}", img)

                session["filename"] = filename
                session["most_common"] = most_common
                session["healthy_num"] = healthy_num
                session["diseased_num"] = diseased_num
                session["healthy_perc"] = healthy_perc
                session["status"] = status
                session["counter"] = counter

                del detector
                return redirect(url_for("result"))
            else:
                flash("No leafs were found, try again with different photo", "danger")

        return {"Status": "File should be png or jpg"}, 400

    return render_template("home.html", form=form)


@app.route("/result", methods=["GET", "POST"])
def result():
    filename = session.get("filename", None)
    if filename and os.path.exists(rf"{config.PROCESSED_IMG_TEMP_PATH}\{filename}"):
        most_common = session.get("most_common", None)
        healthy_num = session.get("healthy_num", None)
        diseased_num = session.get("diseased_num", None)
        healthy_perc = session.get("healthy_perc", None)
        counter = session.get("counter", None)
        status = session.get("status", None)

        full_content_list = []
        tips_indexes = ["One", "Two", "Three", "Four", "Five"]
        diseases_counter = counter.copy()

        try:
            del diseases_counter["Healthy"]
        except KeyError:
            pass

        for index, class_ in enumerate(list(diseases_counter.keys())):
            full_content_list.append([class_, tips_indexes[index], tips_dict[class_.lower()]])

        return render_template("results.html",
                               image=rf"{url_for('static', filename=f'images/tempImages/{filename}')}",
                               healthy_perc=healthy_perc,
                               status=status,
                               most_common=most_common,
                               healthy_num=healthy_num,
                               diseased_num=diseased_num,
                               detected_classes=list(set(counter.keys())),
                               full_content_list=full_content_list)
    else:
        return redirect(url_for("home"))


@app.route("/test/detections", methods=["POST"])
def test_detections():
    image_raw = request.files['image']

    if image_raw.content_type == 'image/jpeg' or image_raw.content_type == 'image/png':
        img = Image.open(image_raw)
        img = np.array(img)
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

        detector = Detector(
            classes_file_path=rf"{MODEL_PATH}/classes.txt",
            weights_file_path=rf"{MODEL_PATH}/yolov3_training_last.weights",
            config_file_path=rf"{MODEL_PATH}/yolov3_testing.cfg",
            confidence_threshold=config.CONFIDENCE_THRESHOLD,
            nms_threshold=config.NMS_THRESHOLD
        )

        detections = detector.detect(img)
        if detections:
            img, counter, most_common, healthy_num, diseased_num, healthy_perc, status = \
                detector.draw_detections(img, detections)
        else:
            status = None

        del detector

        return {"Status": status}, 200
    else:
        return {"Status": "File should be png or jpg"}, 400
