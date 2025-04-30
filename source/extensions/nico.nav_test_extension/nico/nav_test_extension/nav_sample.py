import omni.anim.navigation.core as nav
import carb
import omni.usd
import omni.kit.app
from pxr import UsdGeom, Gf, Sdf, Usd, Tf


class Transform:
    def __init__(self, prim):
        self._xform = UsdGeom.Xformable(prim)
        self._translate_op = self._ensure_xform_ops(self._xform, UsdGeom.XformOp.TypeTranslate)

    @property
    def position(self) -> Gf.Vec3d:
        return self._translate_op.Get()

    @position.setter
    def position(self, value: Gf.Vec3d):
        self._translate_op.Set(value)

    @property
    def position_carb(self) -> carb.Float3:
        pos = self.position
        return carb.Float3(pos[0], pos[1], pos[2])

    @position_carb.setter
    def position_carb(self, value: carb.Float3):
        self.position = Gf.Vec3d(value.x, value.y, value.z)

    def _ensure_xform_ops(self, xform: UsdGeom.Xformable, type: UsdGeom.XformOp):
        for op in xform.GetOrderedXformOps():
            if op.GetOpType() == type:
                return op
        return xform.AddTranslateOp()


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
        print(root_path)
        path = root_path.AppendChild(f"Point_{number}")
        print("path aaaaaaaaaaa")
        print(path)
        sphere: UsdGeom.Sphere = UsdGeom.Sphere.Define(self._stage, path)
        sphere.GetRadiusAttr().Set(10)
        Transform(sphere).position_carb = position


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

        self._actor_transform.position_carb = self._path_points[0]

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
        print(delta_time)

        # current_pos = Gf.Vec3d(translate_op.Get())
        # target_point = self._path_points[0]
        self._actor_transform.position += Gf.Vec3d(0, self._speed, 0) * delta_time
        # translate_op.Set(translate_op.Get() + Gf.Vec3d(0, self._speed, 0) * delta_time)
        # self._move_actor_position(Gf.Vec3d(0, self._speed, 0) * delta_time)

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
