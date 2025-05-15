import carb
import carb.events
import omni.usd
import omni.kit.app
from pxr import UsdGeom,  Sdf, Gf
from .transform import Transform
from . import usdutils
from .path_visualizer import PathVisualizer
from .path_navigator import PathNavigator
from .path_finder import PathFinder
from .polyline import Polyline

def create_sphere(path: str, radius: float):
    stage = usdutils.get_stage()
    sphere: UsdGeom.Sphere = UsdGeom.Sphere.Define(stage, Sdf.Path(path))
    sphere.GetRadiusAttr().Set(radius)
    return sphere

class NavSample:
    def __init__(self):
        self._speed = 50.0

    def start(self):
        self._path_finder = PathFinder.create()

        # self._stage: Usd.Stage|None = cast(Any, omni.usd.get_context()).get_stage()
        self._stage = usdutils.get_stage()

        self._actor = create_sphere("/World/Actor", 50)
        self._actor_transform = Transform(self._actor)
        self._destination = create_sphere("/World/Destination", 80)
        self._destination_transform = Transform(self._destination)
        self._destination_transform.position = Gf.Vec3d(1000, 50, 0)

        path_points = self._path_finder.find(
            Gf.Vec3d(0, 0, 0),
            self._destination_transform.position
        )
        # self._path_visualizer = PathVisualizer(
        #     self._stage,
        #     "/World/PathVisualizer",
        #     path_points
        # )
        self._path_line = Polyline(
            self._stage,
            "/World/PathLine",
            path_points,
            color=Gf.Vec3f(0.3, 0.3, 1))
        self._path_navigator = PathNavigator(path_points)
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

        self._destination = None
        self._destination_transform = None

        self._stage = None
        self._update_sub = None
        # if self._path_visualizer:
        #     self._path_visualizer.destroy()
        # self._path_visualizer = None

    def _on_update(self, e: carb.events.IEvent):
        delta_time = e.payload["dt"]

        assert self._actor_transform
        assert self._destination_transform

        # self._actor_transform.position += Gf.Vec3d(0, self._speed, 0) * delta_time
        self._path_navigator.move_forward(self._speed * delta_time)
        self._actor_transform.position = self._path_navigator.evaluate_current_position()

        self._recalculate_path()

    def _recalculate_path(self):
        assert self._actor_transform
        assert self._destination_transform
        # assert self._path_visualizer
        assert self._path_line

        start_point = self._actor_transform.position
        end_point = self._destination_transform.position

        path_points = self._path_finder.find(
            start_point,
            end_point
        )
        # print(f"path length: {len(path_points)}")
        # self._path_visualizer.update_path(path_points)
        self._path_line.update_points(path_points)
