from multiprocessing.connection import Connection
from src.video_processing.pipeline import touch_processor
from src.video_processing.detection.pose_estimator import PoseEstimator
from src.video_processing.detection.gesture_recognizer import GestureRecognizer
from src.video_processing.detection.hand_detector import HandDetector


def detection_worker(connection: Connection) -> None:
    keypoints_detector = PoseEstimator()
    hand_detector = HandDetector()
    gesture_recognizer = GestureRecognizer()
    # try:
    while True:
        data = connection.recv()
        if data == "stop":
            break
        task_id, img = data
        results = touch_processor(
            frame=img,
            task_ind=task_id,
            keypoints_detector=keypoints_detector,
            hand_detector=hand_detector,
            gesture_recognizer=gesture_recognizer,
            verbose=False,
        )
        connection.send(results.model_dump_json())
    # except EOFError | IndexError:
    #     return
