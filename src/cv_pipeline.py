import cv2
import numpy as np
from ultralytics import YOLO
from video_processing.gesture_recognition import GestureRecognizer
from video_processing.keypoints_detection import KeypointsDetector
from video_processing.gesture_recognition import HandDetector


def main(num_points: int = 1):
    keypoints_detector = KeypointsDetector()
    hand_detector = HandDetector()
    gesture_recognizer = GestureRecognizer()

    cap = cv2.VideoCapture(0)
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            print("Can't receive frame (stream end?). Exiting ...")
            break

        keypoints_results = keypoints_detector.detect_keypoints(frame)
        hands_results = hand_detector.detect_hands(frame)

        cv2.imshow("frame", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
