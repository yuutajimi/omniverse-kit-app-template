import omni.anim.navigation.core as nav
import carb
import omni.usd
import omni.kit.app
from pxr import UsdGeom, Gf, Sdf, Usd, Tf
from .transform import Transform
import math

class PathVisualizer:
    def __init__(self, stage: Usd.Stage, visualize_path: str, path_points: list[carb.Float3]):
        self._stage = stage
        root_path = Sdf.Path(visualize_path)
        self._root = UsdGeom.Xform.Define(stage, root_path)

        for i, point in enumerate(path_points):
            self._create_point(point, i)

    def destroy(self):
        self._stage.RemovePrim(self._root.GetPath())

    def _create_point(self, position: carb.Float3, number: int):
        root_path = self._root.GetPath()
        path = root_path.AppendChild(f"Point_{number}")
        sphere: UsdGeom.Sphere = UsdGeom.Sphere.Define(self._stage, path)
        sphere.GetRadiusAttr().Set(10)
        Transform(sphere).position_carb = position


def float3_add(a: carb.Float3, b: carb.Float3):
    return carb.Float3(
        a.x + b.x,
        a.y + b.y,
        a.z + b.z,
    )


def float3_sub(a: carb.Float3, b: carb.Float3):
    return carb.Float3(
        a.x - b.x,
        a.y - b.y,
        a.z - b.z,
    )

def float3_mul_float(a: carb.Float3, b: float):
    return carb.Float3(
        a.x * b,
        a.y * b,
        a.z * b,
    )

def float3_lerp(a: carb.Float3, b: carb.Float3, t: float):
    offset = float3_sub(b, a)
    offset = float3_mul_float(offset, t)
    return float3_add(a, offset)


def float3_magnitude(v: carb.Float3):
    sum_of_squares = (v.x * v.x) + \
                    (v.y * v.y) + \
                    (v.z * v.z)

    return math.sqrt(sum_of_squares)


class PathNavigator:
    def __init__(self, points: list[carb.Float3]):
        self._points = points
        self._current_distance = 0.0
        self._current_index = 0
        self._current_progress = 0.0
        self._arrival_threshold = 1.0

    @property
    def points(self) -> list[carb.Float3]:
        return self._points

    def evaluate_current_position(self) -> carb.Float3:
        point = self._points[self._current_index]
        if self._current_index < len(self._points) - 1:
            next_point = self._points[self._current_index + 1]
            point = float3_lerp(point, next_point, self._current_progress)

        return point

    def move_forward(self, distance: float):
        while distance > 0:
            if self._current_index >= len(self._points) - 1:
                return

            current_point = self._points[self._current_index]
            next_point = self._points[self._current_index + 1]
            span = float3_magnitude(float3_sub(next_point, current_point))
            distance_rate = distance / span if span > 0 else 1
            remaining_progress = 1 - self._current_progress

            if remaining_progress > distance_rate:
                self._current_progress += distance_rate
                break
            else:
                distance -= span * remaining_progress
                self._current_index += 1
                self._current_progress = 0

        print(f"moved: {self._current_index}: {self._current_progress}")


class NavSample:
    def __init__(self):
        self._speed = 50.0
        self._stage: Usd.Stage = omni.usd.get_context().get_stage()

    def start(self):
        self._path_points = self._find_path()
        if not self._path_points:
            return

        actor_path = Sdf.Path("/World/Actor")
        actor: UsdGeom.Sphere = UsdGeom.Sphere.Define(self._stage, actor_path)
        self._actor = actor
        actor.GetRadiusAttr().Set(50)
        self._actor_transform = Transform(actor)

        self._update_sub = (
            omni.kit.app.get_app()
                .get_update_event_stream()
                .create_subscription_to_pop(
                    self._on_update,
                    name="MoveActorUpdate"
                )
        )

        self._path_visualizer = PathVisualizer(
            self._stage,
            "/World/PathVisualizer",
            self._path_points
        )
        self._path_navigator = PathNavigator(self._path_points)
        self._actor_transform.position_carb = self._path_navigator.evaluate_current_position()


    def stop(self):
        if self._actor:
            # TODO: destroy actor
            # self._actor
            pass

        self._actor = None
        self._actor_transform = None
        self._update_sub = None
        if self._path_visualizer:
            self._path_visualizer.destroy()
        self._path_visualizer = None


    def _on_update(self, e: carb.events.IEvent):
        delta_time = e.payload["dt"]

        # self._actor_transform.position += Gf.Vec3d(0, self._speed, 0) * delta_time
        self._path_navigator.move_forward(self._speed * delta_time)
        self._actor_transform.position_carb = self._path_navigator.evaluate_current_position()

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

        path_points = path_query_result.get_points()
        if not path_points:
            print("failed to get points on the path")
            return

        print(f"path found: {path_points}")

        return path_points
