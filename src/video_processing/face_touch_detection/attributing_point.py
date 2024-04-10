import cv2
from numpy import ndarray


class AttributingPoint:
    def __init__(self, point: tuple[int, int]) -> None:
        x, y = point
        self.bbox = (x - 10, y - 10), (x + 10, y + 10)

    def draw_bbox(self, frame: ndarray) -> None:
        cv2.rectangle(frame, self.bbox[0], self.bbox[1], (0, 0, 255), 2)

    def check_intersection(self, x: int, y: int) -> bool:
        min_x, min_y = self.bbox[0]
        max_x, max_y = self.bbox[1]
        return min_x <= x <= max_x and min_y <= y <= max_y

    def draw_intersection(self, frame: ndarray, ind: int, name_hand: str) -> None:
        x, y = self.bbox[0]
        text = f"Dot {ind}, {name_hand}"
        cv2.putText(
            frame, text, (x, y - 1), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2
        )
