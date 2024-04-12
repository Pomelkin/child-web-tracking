from typing import Tuple


class Hand:
    def __init__(
        self,
        name: str,
        points: list[tuple[int, int]],
        gesture: str,
        bbox: Tuple[int, int, int, int],
    ) -> None:
        self.name = name
        self.points = points
        self.gesture = gesture
        self.bbox = bbox
