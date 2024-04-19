from multiprocessing.connection import Connection
from src.pipeline import detect_action
from src.video_processing.detection.pose_estimator import PoseEstimator
from src.video_processing.detection.gesture_recognizer import GestureRecognizer
from src.video_processing.detection.hand_detector import HandDetector


def detection_worker(connection: Connection) -> None:
    keypoints_detector = PoseEstimator()
    hand_detector = HandDetector()
    gesture_recognizer = GestureRecognizer()
    while True:
        try:
            data = connection.recv()
            if data == "stop":
                break
            keypoint, img = data
            results = detect_action(
                frame=img,
                keypoint_index=keypoint,
                keypoints_detector=keypoints_detector,
                hand_detector=hand_detector,
                gesture_recognizer=gesture_recognizer,
                verbose=False,
            )
            connection.send(results.model_dump_json())
        except EOFError:
            break
    return
