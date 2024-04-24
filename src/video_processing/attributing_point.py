class AttributingPoint:
    def __init__(self, point: tuple[int, int]) -> None:
        x, y = point
        self._bbox = (x - 30, y - 30), (x + 30, y + 30)

    def check_intersection(self, x: int, y: int) -> bool:
        min_x, min_y = self._bbox[0]
        max_x, max_y = self._bbox[1]
        return min_x <= x <= max_x and min_y <= y <= max_y
