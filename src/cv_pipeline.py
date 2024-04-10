import cv2
import numpy as np


def main():
    pose_model = YOLO("src/models/yolov8m-pose.pt")
    hand_model = YOLO("src/models/yolov8m-hand_detector.pt")
    gesture_recognizer = GestureRecognizer()

    cap = cv2.VideoCapture(0)
    while cap.isOpened():
        ret, frame = cap.read()
        cv2.imshow("frame", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
