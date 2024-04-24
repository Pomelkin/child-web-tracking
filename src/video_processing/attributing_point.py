class AttributingPoint:
    def __init__(self, point: tuple[int, int]) -> None:
        x, y = point
        self._bbox = (x - 20, y - 20), (x + 20, y + 20)

    def check_intersection(self, x: int, y: int) -> bool:
        min_x, min_y = self._bbox[0]
        max_x, max_y = self._bbox[1]
        return min_x <= x <= max_x and min_y <= y <= max_y
