import numpy as np
from src.video_processing.detection.pose_estimator import PoseEstimator
from src.video_processing.detection.gesture_recognizer import GestureRecognizer
from src.video_processing.detection.hand_detector import HandDetector
from src.video_processing import Hand, AttributingPoint
from src.schemas import DetectionTaskResponse, DetectionTaskError


def detect_action(
    frame: np.ndarray,
    keypoint_index: int,
    keypoints_detector: PoseEstimator,
    hand_detector: HandDetector,
    gesture_recognizer: GestureRecognizer,
    verbose: bool = False,
) -> DetectionTaskResponse:
    # constants
    error_count_prompts = ["too little", "too much"]

    # keypoints and hands detection keypoints_results hand_results
    keypoints_results = keypoints_detector.detect_keypoints(
        frame=frame, verbose=verbose
    )[0]
    hand_results = hand_detector.detect_hands(frame=frame, verbose=verbose)[0]

    # person count validation
    if (person_count := len(keypoints_results.boxes.data.tolist())) != 1:
        error_count = 0 if person_count == 0 else 1

        persons_count_error = DetectionTaskResponse(
            success=False,
            error=DetectionTaskError(
                error=True, message=f"{error_count_prompts[error_count]} people"
            ),
        )
        return persons_count_error

    # extracting attributing point coordinates
    points = keypoints_results.keypoints.xy.tolist()[0]
    x, y = tuple(map(int, points[keypoint_index]))
    if (x and y) == 0:
        keypoint_error = DetectionTaskResponse(
            success=False,
            error=DetectionTaskError(error=True, message="keypoint is not detected"),
        )
        return keypoint_error

    attributing_point = AttributingPoint((x, y))

    # extracting hands keypoints and gestures
    hands = []
    for hand_bbox in hand_results.boxes.data.tolist():
        x1, y1, x2, y2, score, class_id = hand_bbox

        hand_frame = frame[int(y1 * 0.8) : int(y2 * 1.2), int(x1 * 0.8) : int(x2 * 1.2)]
        width, height = int(hand_frame.shape[1]), int(hand_frame.shape[0])
        hand_result = gesture_recognizer.recognize_gesture(hand_frame)

        if len(hand_result.hand_landmarks) == 0:
            continue

        points = []
        hand = hand_result.hand_landmarks[0]
        name = hand_result.handedness[0][0].category_name
        gesture = hand_result.gestures[0][0].category_name
        for ind, point in enumerate(hand):
            # skipping extra points
            if ind % 4 != 0:
                continue

            x, y = int(point.x * width + x1 * 0.8), int(point.y * height + y1 * 0.8)
            points.append((x, y))

        hands.append(Hand(name, points, gesture, (int(x1), int(y1), int(x2), int(y2))))

    # checking intersection with attributing point
    for hand in hands:
        if len(points := hand.points) == 0:
            continue
        for ind, point in enumerate(points):
            x, y = point
            if attributing_point.check_intersection(x, y):
                success = DetectionTaskResponse(
                    success=True,
                    error=DetectionTaskError(error=False, message=""),
                )
                return success

    failure = DetectionTaskResponse(
        success=False,
        error=DetectionTaskError(error=False, message=""),
    )
    return failure
