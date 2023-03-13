from collections import Counter
import cv2

from TomatoLeafs.webapp.detector import Detector

detector = Detector(
    weights_file_path=r"webapp/model/yolov3_training_last.weights",
    config_file_path=r"webapp/model/yolov3_testing.cfg",
    classes_file_path=r"webapp/model/classes.txt",
    confidence_threshold=.1,
    nms_threshold=.5
)


leafs_list = []

image_mode = True
if image_mode:
    img = cv2.imread(r"medias/test12.png")

    detections = detector.detect(img)
    for detection in detections:
        x1, y1 = detection.x, detection.y
        x2, y2 = detection.x + detection.w, detection.y + detection.h

        print(int(round(detection.detections_conf, 2) * 100))
        cv2.rectangle(img, (x1, y1), (x2, y2), detection.color, 2)
        cv2.putText(img, f"{detection.class_name} {int(round(detection.detections_conf, 2) * 100)}%",
                    (x1, y1 - 15), cv2.FONT_HERSHEY_PLAIN, 1.5, detection.color, 2)
        leafs_list.append(detection.class_name)

    leaf_counter = Counter(leafs_list)
    # print(list(leaf_counter.items())[0])
    print(list(leaf_counter.items()))
    print(max(list(leaf_counter.items())))
    print(max(leaf_counter, key=leaf_counter.get))
    cv2.imshow("resImage", img)
    cv2.waitKey(0)
