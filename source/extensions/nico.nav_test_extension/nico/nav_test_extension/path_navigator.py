from pxr import  Gf
from . import omath

class PathNavigator:
    def __init__(self, points: list[Gf.Vec3d]):
        self._points = points
        self._current_distance = 0.0
        self._current_index = 0
        self._current_progress = 0.0
        self._arrival_threshold = 1.0

    @property
    def points(self) -> list[Gf.Vec3d]:
        return self._points

    def evaluate_current_position(self) -> Gf.Vec3d:
        point = self._points[self._current_index]
        if self._current_index < len(self._points) - 1:
            next_point = self._points[self._current_index + 1]
            point = omath.lerp(point, next_point, self._current_progress)

        return point

    def move_forward(self, distance: float):
        while distance > 0:
            if self._current_index >= len(self._points) - 1:
                return

            current_point = self._points[self._current_index]
            next_point = self._points[self._current_index + 1]
            span = omath.length(next_point - current_point)
            distance_rate = distance / span if span > 0 else 1
            remaining_progress = 1 - self._current_progress

            if remaining_progress > distance_rate:
                self._current_progress += distance_rate
                break
            else:
                distance -= span * remaining_progress
                self._current_index += 1
                self._current_progress = 0

        # print(f"moved: {self._current_index}: {self._current_progress}")
