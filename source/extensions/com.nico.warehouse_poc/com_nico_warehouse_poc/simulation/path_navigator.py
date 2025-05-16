# (ユーザー提供のファイルをそのまま配置、omath.lengthの修正を考慮)
from pxr import  Gf
from ..utils import omath # Changed from "from . import omath"

class PathNavigator:
    def __init__(self, points: list[Gf.Vec3d]):
        if not points or len(points) < 1: # Path must have at least one point
            raise ValueError("Path points cannot be empty.")
        self._points = points
        self._current_distance = 0.0
        self._current_index = 0
        self._current_progress = 0.0 # Progress along the current segment (0.0 to 1.0)
        # self._arrival_threshold = 1.0 # Not currently used, but could be for 'near enough' logic

    @property
    def points(self) -> list[Gf.Vec3d]:
        return self._points

    @property
    def is_finished(self) -> bool:
        """Checks if the navigator has reached the end of the path."""
        return self._current_index >= len(self._points) - 1 and self._current_progress >= 1.0

    def evaluate_current_position(self) -> Gf.Vec3d:
        # If only one point or already past the last segment, return the last point
        if len(self._points) == 1 or self._current_index >= len(self._points) -1:
            return self._points[-1]

        current_segment_start_point = self._points[self._current_index]
        current_segment_end_point = self._points[self._current_index + 1]

        # Interpolate position along the current segment
        return omath.lerp(current_segment_start_point, current_segment_end_point, self._current_progress)


    def move_forward(self, distance: float):
        if distance <= 0:
            return
        if self.is_finished: # Already at the end
            return

        remaining_distance_to_move = distance

        while remaining_distance_to_move > 0 and not self.is_finished:
            if self._current_index >= len(self._points) - 1: # Should be caught by is_finished, but defensive
                self._current_progress = 1.0 # Ensure it's marked as finished
                break

            current_segment_start = self._points[self._current_index]
            current_segment_end = self._points[self._current_index + 1]
            segment_vector = current_segment_end - current_segment_start
            segment_length = omath.length(segment_vector) # Assuming omath.length takes Gf.Vec3d

            # Distance remaining in the current segment
            distance_left_in_segment = segment_length * (1.0 - self._current_progress)

            if remaining_distance_to_move >= distance_left_in_segment:
                # Move to the end of the current segment and consume that distance
                remaining_distance_to_move -= distance_left_in_segment
                self._current_index += 1
                self._current_progress = 0.0 # Reset progress for the new segment
                if self._current_index >= len(self._points) - 1: # Reached the end of the path
                    self._current_progress = 1.0 # Mark as fully at the end
                    break
            else:
                # Move partially along the current segment
                if segment_length > 1e-6: # Avoid division by zero for zero-length segments
                    progress_to_add = remaining_distance_to_move / segment_length
                    self._current_progress += progress_to_add
                remaining_distance_to_move = 0 # All requested distance consumed
                break