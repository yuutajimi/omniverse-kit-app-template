import omni.anim.navigation.core as nav
import carb
import carb.events
import omni.usd
import omni.kit.app
from pxr import UsdGeom, Gf, Sdf, Usd, Tf
from .transform import Transform
from typing import Any, cast
from . import omath

class PathVisualizer:
    def __init__(self, stage: Usd.Stage, visualize_path: str, path_points: list[Gf.Vec3d]):
        self._stage = stage
        root_path = Sdf.Path(visualize_path)
        self._root = UsdGeom.Xform.Define(stage, root_path)

        for i, point in enumerate(path_points):
            self._create_point(point, i)

    def destroy(self):
        self._stage.RemovePrim(self._root.GetPath())

    def _create_point(self, position: Gf.Vec3d, number: int):
        root_path = self._root.GetPath()
        path = root_path.AppendChild(f"Point_{number}")
        sphere: UsdGeom.Sphere = UsdGeom.Sphere.Define(self._stage, path)
        sphere.GetRadiusAttr().Set(10)
        Transform(sphere).position = position



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


class NavSample:
    def __init__(self):
        self._speed = 50.0

    def start(self):
        self._path_points = self._find_path()
        if not self._path_points:
            return

        # self._stage: Usd.Stage|None = cast(Any, omni.usd.get_context()).get_stage()
        self._stage: Usd.Stage|None = omni.usd.get_context().get_stage()

        actor_path = Sdf.Path("/World/Actor")
        actor: UsdGeom.Sphere = UsdGeom.Sphere.Define(self._stage, actor_path)
        self._actor = actor
        actor.GetRadiusAttr().Set(50)
        self._actor_transform = Transform(actor)

        self._path_visualizer = PathVisualizer(
            self._stage,
            "/World/PathVisualizer",
            self._path_points
        )
        self._path_navigator = PathNavigator(self._path_points)
        self._actor_transform.position = self._path_navigator.evaluate_current_position()

        self._update_sub = (
            omni.kit.app.get_app()
                .get_update_event_stream()
                .create_subscription_to_pop(
                    self._on_update,
                    name="MoveActorUpdate"
                )
        )



    def stop(self):
        if self._actor:
            # TODO: destroy actor
            # self._actor
            pass

        self._actor = None
        self._actor_transform = None
        self._stage = None
        self._update_sub = None
        if self._path_visualizer:
            self._path_visualizer.destroy()
        self._path_visualizer = None


    def _on_update(self, e: carb.events.IEvent):
        delta_time = e.payload["dt"]

        assert self._actor_transform

        # self._actor_transform.position += Gf.Vec3d(0, self._speed, 0) * delta_time
        self._path_navigator.move_forward(self._speed * delta_time)
        self._actor_transform.position = self._path_navigator.evaluate_current_position()


    def _find_path(self):
        inav = nav.acquire_interface()
        navmesh = inav.get_navmesh()

        if not navmesh:
            print("NavMesh not found or not baked")
            return

        start_pos = carb.Float3(0, 0, 0)
        end_pos = carb.Float3(1000, 50, 0)

        path_query_result = navmesh.query_shortest_path(
            start_pos=start_pos,
            end_pos=end_pos
        )

        if not path_query_result:
            print("Path not found")
            return

        path_points: list[carb.Float3]|None = path_query_result.get_points()
        if not path_points:
            print("failed to get points on the path")
            return

        print(f"path found: {path_points}")

        return [
            omath.to_gf(v)
            for v in path_points
        ]
