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


class NavSample:
    def __init__(self):
        self._speed = 50.0

    def start(self):
        self._path_finder = PathFinder.create()

        # self._stage: Usd.Stage|None = cast(Any, omni.usd.get_context()).get_stage()
        self._stage = usdutils.get_stage()

        actor_path = Sdf.Path("/World/Actor")
        actor: UsdGeom.Sphere = UsdGeom.Sphere.Define(self._stage, actor_path)
        self._actor = actor
        actor.GetRadiusAttr().Set(50)
        self._actor_transform = Transform(actor)

        path_points = self._path_finder.find(
            Gf.Vec3d(0, 0, 0),
            Gf.Vec3d(1000, 50, 0)
        )
        self._path_visualizer = PathVisualizer(
            self._stage,
            "/World/PathVisualizer",
            path_points
        )
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
