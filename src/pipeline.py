import cv2
import numpy as np
from ultralytics import YOLO
from video_processing.detection.pose_estimator import PoseEstimator
from video_processing.detection.gesture_recognizer import GestureRecognizer
from video_processing.detection.hand_detector import HandDetector
from video_processing import Hand, AttributingPoint


def main(keypoint_index: int = 0):
    # constants
    error_count_prompts = ["too little", "too much"]

    # models initialization
    keypoints_detector = PoseEstimator()
    hand_detector = HandDetector()
    gesture_recognizer = GestureRecognizer()

    cap = cv2.VideoCapture(0)
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            print("Can't receive frame (stream end?). Exiting ...")
            break

        # keypoints and hands detection
        keypoints_results = keypoints_detector.detect_keypoints(frame)[0]
        hand_results = hand_detector.detect_hands(frame)[0]

        # person count validation
        if (person_count := len(keypoints_results.boxes.data.tolist())) != 1:
            error_ind = person_count != 0
            print(f"Error, {error_count_prompts[error_ind]} people")
            continue

        # extracting attributing point coordinates
        points = keypoints_results.keypoints.xy.tolist()[0]
        x, y = tuple(map(int, points[keypoint_index]))
        if (x and y) == 0:
            continue
        attributing_point = AttributingPoint((x, y))

        # extracting hands keypoints and gestures
        hands = []
        for hand_bbox in hand_results.boxes.data.tolist():
            x1, y1, x2, y2, score, class_id = hand_bbox

            hand_frame = frame[
                int(y1 * 0.8) : int(y2 * 1.2), int(x1 * 0.8) : int(x2 * 1.2)
            ]
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

            hands.append(
                Hand(name, points, gesture, (int(x1), int(y1), int(x2), int(y2)))
            )

            cv2.rectangle(
                frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), thickness=2
            )
            cv2.putText(
                frame,
                f"{name}, {gesture}",
                (int(x1), int(y1 - 2)),
                cv2.FONT_ITALIC,
                0.6,
                (0, 255, 0),
                1,
            )

        # checking intersection with attributing point
        for hand in hands:
            if len(points := hand.points) == 0:
                continue
            for ind, point in enumerate(points):
                x, y = point
                cv2.putText(
                    frame,
                    str(ind),
                    (x, y),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (255, 255, 0),
                    1,
                )
                cv2.circle(frame, (x, y), 3, (0, 0, 255), -1)

                if attributing_point.check_intersection(x, y):
                    print(f"Yep, {hand.name}")

        cv2.imshow("frame", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
