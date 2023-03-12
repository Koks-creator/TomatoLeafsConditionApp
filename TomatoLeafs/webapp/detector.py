from dataclasses import dataclass
from typing import List
import cv2
import numpy as np
from collections import Counter


np.random.seed(0)


@dataclass
class DetectionData:
    x: int
    y: int
    w: int
    h: int
    class_name: str
    detections_conf: float
    color: list


@dataclass
class Detector:
    weights_file_path: str
    config_file_path: str
    classes_file_path: str
    image_width: int = 416
    image_height: int = 416
    confidence_threshold: float = 0.3
    nms_threshold: float = 0.3

    def __post_init__(self) -> None:
        self.net = cv2.dnn.readNet(self.weights_file_path, self.config_file_path)
        layer_names = self.net.getLayerNames()
        self.output_layers = [layer_names[i[0] - 1] for i in self.net.getUnconnectedOutLayers()]

        with open(self.classes_file_path) as f:
            self.classes = f.read().splitlines()

        self.colors = np.random.uniform(0, 255, size=(len(self.classes), 3))

    def detect(self, img: np.array) -> List[DetectionData]:
        """
        :param img: input img
        :return: list of tuples containing the following data: x, y, w, h, class_name, confidence, class_color
        """
        bbox = []
        class_ids = []
        confs = []

        height, width, _ = img.shape

        blob = cv2.dnn.blobFromImage(img, 1/255, (self.image_width, self.image_height), (0, 0, 0), True, crop=False)

        self.net.setInput(blob)
        outs = self.net.forward(self.output_layers)

        for out in outs:
            for detection in out:
                scores = detection[5:]
                class_id = np.argmax(scores)
                # print(class_id)
                confidence = scores[class_id]

                if confidence > self.confidence_threshold:
                    w = int(detection[2] * width)
                    h = int(detection[3] * height)
                    x = int((detection[0] * width) - w/2)
                    y = int((detection[1] * height) - h/2)

                    bbox.append([x, y, w, h])
                    class_ids.append(class_id)
                    confs.append(float(confidence))

        indexes = cv2.dnn.NMSBoxes(bbox, confs, self.confidence_threshold, self.nms_threshold)

        detections_list = []
        for i in indexes:
            i = i[0]

            box = bbox[i]
            x, y, w, h = box
            class_name = self.classes[class_ids[i]].capitalize()
            conf = confs[i]
            class_color = [int(c) for c in self.colors[class_ids[i]]]

            detections_list.append(DetectionData(x, y, w, h, class_name, conf, class_color))

        return detections_list

    @staticmethod
    def draw_detections(img: np.array, detections: List[DetectionData]) -> tuple:
        detected_classes = []

        for detection in detections:
            x1, y1 = detection.x, detection.y
            x2, y2 = detection.x + detection.w, detection.y + detection.h

            cv2.rectangle(img, (x1, y1), (x2, y2), detection.color, 1)
            cv2.rectangle(img, (x1, y1), (x2, y1-20), detection.color, -1)
            cv2.putText(img, f"{detection.class_name} {int(round(detection.detections_conf, 2) * 100)}%",
                        (x1, y1-5), cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 255), 1)

            detected_classes.append(detection.class_name)

        if detected_classes:
            counter = Counter(detected_classes)
            most_common = max(counter, key=counter.get)

            healthy_num = counter["Healthy"]
            diseased_num = sum([item[1] for item in counter.items() if item[0] != "Healthy"])

            healthy_perc = round(healthy_num * 100 / (healthy_num + diseased_num), 2)

            status = ""

            if healthy_perc > 90:
                status = "Healthy"
            elif 75 < healthy_perc < 90:
                status = "Mostly Healthy"
            elif 60 < healthy_perc < 75:
                status = "Disease occurrence"
            elif 40 < healthy_perc < 60:
                status = "Diseased"
            elif healthy_perc < 40:
                status = "Very Diseased!"

            return img, counter, most_common, healthy_num, diseased_num, healthy_perc, status


if __name__ == '__main__':
    detector = Detector(
        classes_file_path=r"model/classes.txt",
        weights_file_path="model/yolov3_training_last.weights",
        config_file_path="model/yolov3_testing.cfg",
        confidence_threshold=.1,
        nms_threshold=.1
    )

    img = cv2.imread("../medias/mixed3.png")

    detections = detector.detect(img)
    img, counter, most_common, healthy_num, diseased_num, healthy_perc, status = detector.draw_detections(img, detections)

    cv2.imshow("res", img)
    cv2.waitKey(0)
